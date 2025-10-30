"""Analyze random Jeep dealer contact forms for field coverage and dropdown rules."""

from __future__ import annotations

import argparse
import asyncio
import csv
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector, EnhancedFormField

RESULT_GLOB = ROOT / "tests" / "final_retest_contact_urls_*" / "final_retest_results.csv"


@dataclass
class DealerRecord:
    name: str
    contact_url: str


@dataclass
class DropdownDecision:
    label: str
    selector: str
    decision_type: str
    chosen_option: Optional[str]
    rationale: str
    options: List[str]


@dataclass
class CheckboxDecision:
    label: str
    selector: str
    action: str = "check"


def load_candidates(limit: int, seed: int = 42) -> List[DealerRecord]:
    rows: List[DealerRecord] = []
    seen_urls = set()
    for csv_path in sorted(ROOT.glob("tests/final_retest_contact_urls_*/final_retest_results.csv")):
        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                contact_url = row.get("contact_url", "").strip()
                if not contact_url or contact_url in seen_urls:
                    continue
                status = (row.get("final_retest_status") or "").strip().lower()
                if status != "success":
                    continue
                dealer_name = row.get("dealer_name", "Dealer").strip()
                rows.append(DealerRecord(name=dealer_name, contact_url=contact_url))
                seen_urls.add(contact_url)

    if len(rows) < limit:
        jeep_csv = ROOT / "Dealerships - Jeep.csv"
        if jeep_csv.exists():
            with jeep_csv.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    website = (row.get("website") or "").strip()
                    dealer_name = (row.get("dealer_name") or "Dealer").strip()
                    if not website:
                        continue
                    if not website.startswith("http"):
                        website = "https://" + website.lstrip("/")
                    if not website.endswith("/"):
                        website = website + "/"
                    contact_url = urljoin(website, "contact-us/")
                    if contact_url in seen_urls:
                        continue
                    rows.append(DealerRecord(name=dealer_name, contact_url=contact_url))
                    seen_urls.add(contact_url)
                    if len(rows) >= limit:
                        break

    if len(rows) < limit:
        raise RuntimeError(f"Only found {len(rows)} successful contact URLs; need {limit}.")
    random.seed(seed)
    return random.sample(rows, limit)


async def collect_dropdowns(form_locator) -> List[Dict[str, object]]:
    try:
        return await form_locator.evaluate(
            """
            (form) => {
                const results = [];
                const selects = Array.from(form.querySelectorAll('select'));
                const dedupe = new Set();

                const resolveLabel = (element) => {
                    const id = element.id;
                    if (id) {
                        const label = form.querySelector(`label[for="${CSS.escape(id)}"]`);
                        if (label && label.textContent) {
                            return label.textContent.trim();
                        }
                    }
                    const wrappers = ['.gfield', '.field', '.form-group', '.form-field', 'li', 'div'];
                    for (const selector of wrappers) {
                        const wrap = element.closest(selector);
                        if (wrap) {
                            const label = wrap.querySelector('label');
                            if (label && label.textContent) {
                                return label.textContent.trim();
                            }
                        }
                    }
                    if (element.parentElement) {
                        const label = element.parentElement.querySelector('label');
                        if (label && label.textContent) {
                            return label.textContent.trim();
                        }
                    }
                    return '';
                };

                for (const select of selects) {
                    const key = select.id || select.name || select.outerHTML;
                    if (dedupe.has(key)) continue;
                    dedupe.add(key);

                    const label = resolveLabel(select);
                    const options = Array.from(select.options || []).map(opt => opt.textContent ? opt.textContent.trim() : '').filter(text => text);
                    results.push({
                        id: select.id || null,
                        name: select.name || null,
                        label,
                        options,
                        multiple: !!select.multiple,
                    });
                }
                return results;
            }
            """
        )
    except Exception:
        return []


async def collect_checkboxes(form_locator) -> List[Dict[str, str]]:
    try:
        return await form_locator.evaluate(
            """
            (form) => {
                const checkboxes = Array.from(form.querySelectorAll('input[type="checkbox"]'));
                const results = [];

                const resolveLabel = (element) => {
                    const id = element.id;
                    if (id) {
                        const label = form.querySelector(`label[for="${CSS.escape(id)}"]`);
                        if (label && label.textContent) {
                            return label.textContent.trim();
                        }
                    }
                    const wrappers = ['.gfield', '.field', '.form-group', '.form-field', 'li', 'div'];
                    for (const selector of wrappers) {
                        const wrap = element.closest(selector);
                        if (wrap) {
                            const label = wrap.querySelector('label');
                            if (label && label.textContent) {
                                return label.textContent.trim();
                            }
                        }
                    }
                    if (element.parentElement) {
                        const label = element.parentElement.querySelector('label');
                        if (label && label.textContent) {
                            return label.textContent.trim();
                        }
                    }
                    return '';
                };

                for (const checkbox of checkboxes) {
                    const label = resolveLabel(checkbox);
                    results.push({
                        'id': checkbox.id || null,
                        'name': checkbox.name || null,
                        'label': label,
                    });
                }
                return results;
            }
            """
        )
    except Exception:
        return []


def classify_dropdown(dropdown: Dict[str, object]) -> DropdownDecision:
    label = (dropdown.get("label") or "").strip()
    label_norm = label.lower()
    options = [opt.strip() for opt in dropdown.get("options", []) if opt.strip()]
    opts_norm = [opt.lower() for opt in options]

    selector = ""
    if dropdown.get("id"):
        selector = f"#{dropdown['id']}"
    elif dropdown.get("name"):
        selector = f"select[name='{dropdown['name']}']"

    decision_type = "generic"
    chosen_option: Optional[str] = None
    rationale = "No forced selection; informational only."

    def pick_option(keywords: List[str]) -> Optional[str]:
        for keyword in keywords:
            for opt, norm in zip(options, opts_norm):
                if keyword in norm:
                    return opt
        return None

    contact_keywords = ["contact", "reach", "method", "preferred", "response", "communicat", "best way"]
    reason_keywords = ["reason", "department", "category", "concern", "inquiry", "topic", "subject"]

    if any(word in label_norm for word in contact_keywords) or (
        set(opts_norm) & {"phone", "email", "text"} or any("call" in opt for opt in opts_norm)
    ):
        decision_type = "contact_preference"
        choice = pick_option(["text", "sms", "message"])
        if not choice:
            choice = pick_option(["phone", "call", "telephone"])
        if not choice:
            choice = pick_option(["email"])
        chosen_option = choice
        rationale = (
            "Choose 'text/sms' when available, otherwise 'phone/call', else 'email'."
            if choice
            else "Contact preference dropdown but no matching option found."
        )
    elif any(word in label_norm for word in reason_keywords) or any("sales" in opt for opt in opts_norm):
        decision_type = "contact_reason"
        choice = pick_option(["sales", "new", "purchase", "vehicle", "buy"])
        chosen_option = choice
        rationale = (
            "Choose 'sales' or closest equivalent (new/purchase/vehicle)."
            if choice
            else "Reason dropdown but no sales-related option detected."
        )

    return DropdownDecision(
        label=label or "(unlabeled select)",
        selector=selector or "(unknown selector)",
        decision_type=decision_type,
        chosen_option=chosen_option,
        rationale=rationale,
        options=options,
    )


def summarize_fields(fields: Dict[str, EnhancedFormField]) -> List[str]:
    lines = []
    for field_type, field in sorted(fields.items()):
        lines.append(f"- {field_type}: {field.selector}")
    return lines


def summarize_dropdowns(dropdowns: List[DropdownDecision]) -> List[str]:
    lines: List[str] = []
    if not dropdowns:
        lines.append("- none detected")
        return lines
    for dropdown in dropdowns:
        chosen = dropdown.chosen_option or "(no matching option)"
        lines.append(
            f"- {dropdown.label} ({dropdown.decision_type}): choose '{chosen}' -- {dropdown.rationale}\n"
            f"  selector: {dropdown.selector}\n"
            f"  options: {', '.join(dropdown.options) if dropdown.options else 'no options parsed'}"
        )
    return lines


def summarize_checkboxes(checkboxes: List[CheckboxDecision]) -> List[str]:
    if not checkboxes:
        return ["- none detected"]
    return [
        f"- {cb.label or '(unlabeled checkbox)'}: {cb.action} (selector: {cb.selector})"
        for cb in checkboxes
    ]


async def _find_contact_fallback(page, original_url: str) -> Optional[str]:
    """Try to locate an alternative contact link from the homepage."""

    parsed = urlparse(original_url)
    if not parsed.scheme or not parsed.netloc:
        return None

    home_url = f"{parsed.scheme}://{parsed.netloc}/"

    try:
        await page.goto(home_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
    except PlaywrightTimeoutError:
        return None

    try:
        contact_href = await page.evaluate(
            """
            () => {
                const anchors = Array.from(document.querySelectorAll('a[href]'));
                for (const anchor of anchors) {
                    const text = (anchor.textContent || '').toLowerCase();
                    const href = anchor.getAttribute('href') || '';
                    if (text.includes('contact') || href.toLowerCase().includes('contact')) {
                        return anchor.href;
                    }
                }
                return null;
            }
            """
        )
        if contact_href and contact_href != original_url:
            return contact_href
    except Exception:
        return None

    return None


async def analyze_dealer(detector: EnhancedFormDetector, manager: EnhancedStealthBrowserManager, dealer: DealerRecord) -> Dict[str, object]:
    async with async_playwright() as playwright_instance:
        browser, context = await manager.open_context(playwright_instance)
        page = await manager.create_enhanced_stealth_page(context)

        async def detect(url: str) -> Dict[str, object]:
            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                status = response.status if response else None
                await asyncio.sleep(2)
            except PlaywrightTimeoutError:
                return {"status": "timeout", "result": None}

            detection = await detector.detect_contact_form(page)
            success = detection.success and detection.form_element is not None
            if success:
                return {"status": "success", "result": detection}

            # Flag 404 or empty responses for fallback consideration
            if status == 404 or status == 410:
                return {"status": "not_found", "result": None}

            return {"status": "no_form", "result": detection}

        try:
            primary_detection = await detect(dealer.contact_url)

            if primary_detection["status"] == "success":
                detection = primary_detection["result"]
                final_url = dealer.contact_url
            elif primary_detection["status"] in {"timeout", "no_form"}:
                fallback_url = await _find_contact_fallback(page, dealer.contact_url)
                if fallback_url:
                    fallback_detection = await detect(fallback_url)
                    if fallback_detection["status"] == "success":
                        detection = fallback_detection["result"]
                        final_url = fallback_url
                    else:
                        return {
                            "dealer": dealer.name,
                            "url": fallback_url,
                            "status": fallback_detection["status"],
                            "fields": [],
                            "dropdowns": [],
                            "checkboxes": [],
                        }
                else:
                    return {
                        "dealer": dealer.name,
                        "url": dealer.contact_url,
                        "status": primary_detection["status"],
                        "fields": [],
                        "dropdowns": [],
                        "checkboxes": [],
                    }
            elif primary_detection["status"] == "not_found":
                fallback_url = await _find_contact_fallback(page, dealer.contact_url)
                if fallback_url:
                    fallback_detection = await detect(fallback_url)
                    if fallback_detection["status"] == "success":
                        detection = fallback_detection["result"]
                        final_url = fallback_url
                    else:
                        return {
                            "dealer": dealer.name,
                            "url": fallback_url,
                            "status": fallback_detection["status"],
                            "fields": [],
                            "dropdowns": [],
                            "checkboxes": [],
                        }
                else:
                    return {
                        "dealer": dealer.name,
                        "url": dealer.contact_url,
                        "status": "not_found",
                        "fields": [],
                        "dropdowns": [],
                        "checkboxes": [],
                    }
            else:
                return {
                    "dealer": dealer.name,
                    "url": dealer.contact_url,
                    "status": primary_detection["status"],
                    "fields": [],
                    "dropdowns": [],
                    "checkboxes": [],
                }

            dropdown_raw = await collect_dropdowns(detection.form_element)
            dropdowns = [classify_dropdown(entry) for entry in dropdown_raw]

            checkbox_raw = await collect_checkboxes(detection.form_element)
            checkbox_decisions: List[CheckboxDecision] = []
            for entry in checkbox_raw:
                selector = ""
                if entry.get("id"):
                    selector = f"#{entry['id']}"
                elif entry.get("name"):
                    selector = f"input[name='{entry['name']}']"
                checkbox_decisions.append(
                    CheckboxDecision(label=entry.get("label") or "(unlabeled)", selector=selector or "(unknown selector)")
                )

            return {
                "dealer": dealer.name,
                "url": final_url,
                "status": "success",
                "fields": summarize_fields(detection.fields),
                "dropdowns": summarize_dropdowns(dropdowns),
                "checkboxes": summarize_checkboxes(checkbox_decisions),
            }
        except Exception:
            return {
                "dealer": dealer.name,
                "url": dealer.contact_url,
                "status": "error",
                "fields": [],
                "dropdowns": [],
                "checkboxes": [],
            }
        finally:
            await page.close()
            await manager.close_context(browser, context)


async def main(limit: int, seed: int) -> None:
    candidates = load_candidates(limit=limit, seed=seed)
    detector = EnhancedFormDetector()
    manager = EnhancedStealthBrowserManager()

    results: List[Dict[str, object]] = []
    for dealer in candidates:
        analysis = await analyze_dealer(detector, manager, dealer)
        results.append(analysis)

    for idx, result in enumerate(results, start=1):
        print(f"#{idx} {result['dealer']}")
        print(f"Contact URL: {result['url']}")
        print(f"Detection Status: {result['status']}")
        print("Detected Fields:")
        for line in result["fields"]:
            print(f"  {line}")
        print("Dropdowns:")
        for line in result["dropdowns"]:
            print(f"  {line}")
        print("Checkboxes:")
        for line in result["checkboxes"]:
            print(f"  {line}")
        print("-" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze random Jeep dealer contact forms")
    parser.add_argument("--limit", type=int, default=10, help="Number of dealers to analyze")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    asyncio.run(main(limit=args.limit, seed=args.seed))
