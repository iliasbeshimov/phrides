"""Form submission runner that builds on EnhancedFormDetector to populate and submit contact forms."""

from __future__ import annotations

import asyncio
import json
import os
import re
import random
from dataclasses import dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from playwright.async_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, async_playwright

import sys
ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import Config
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.browser.cloudflare_stealth_config import CloudflareStealth
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector, EnhancedFormResult, EnhancedFormField
from src.automation.navigation.human_behaviors import DEFAULT_BEHAVIOR, HumanBehaviorConfig, warm_up_and_navigate
from src.services.contact.contact_page_cache import ContactPageResolver


@dataclass
class ContactPayload:
    first_name: str
    last_name: str
    email: str
    phone: str
    zip_code: str
    message: str


@dataclass
class SubmissionArtifacts:
    base_dir: Path
    detection: Optional[Path] = None
    filled: Optional[Path] = None
    submitted: Optional[Path] = None
    log: Optional[Path] = None

    def ensure_dirs(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class SubmissionStatus:
    dealer: str
    url: str
    status: str = "pending"
    fields_filled: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    dropdown_choices: Dict[str, str] = field(default_factory=dict)
    checkboxes_checked: List[str] = field(default_factory=list)
    confirmation_text: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    contact_resolution_source: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({
            "dealer": self.dealer,
            "url": self.url,
            "status": self.status,
            "contact_resolution_source": self.contact_resolution_source,
            "fields_filled": self.fields_filled,
            "missing_fields": self.missing_fields,
            "dropdown_choices": self.dropdown_choices,
            "checkboxes_checked": self.checkboxes_checked,
            "confirmation_text": self.confirmation_text,
            "artifacts": self.artifacts,
            "errors": self.errors,
        }, indent=2)


class FormSubmissionRunner:
    """End-to-end helper for detecting, populating, and submitting dealer forms."""

    def __init__(
        self,
        headless: bool = False,  # Default to headful for better Cloudflare evasion
        screenshot_root: Path | None = None,
        behavior_config: HumanBehaviorConfig = DEFAULT_BEHAVIOR,
        use_cloudflare_stealth: bool = True,  # New option for Cloudflare evasion
    ) -> None:
        self.detector = EnhancedFormDetector()
        self.browser_manager = EnhancedStealthBrowserManager()
        self.cloudflare_stealth = (
            CloudflareStealth(
                user_data_dir=Config.AUTO_CONTACT_USER_DATA_DIR,
                browser_channel=Config.AUTO_CONTACT_BROWSER_CHANNEL,
            )
            if use_cloudflare_stealth
            else None
        )
        self.headless = headless
        self.screenshot_root = screenshot_root or Path("artifacts")
        self.behavior_config = behavior_config

    async def run(
        self,
        dealer_name: str,
        url: Optional[str],
        payload: ContactPayload,
        *,
        homepage_url: Optional[str] = None,
        resolver: Optional[ContactPageResolver] = None,
    ) -> SubmissionStatus:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        slug = re.sub(r"[^a-z0-9]+", "_", dealer_name.lower()).strip("_") or "dealer"
        artifact_dir = self.screenshot_root / timestamp / slug
        artifacts = SubmissionArtifacts(base_dir=artifact_dir)
        artifacts.ensure_dirs()

        status = SubmissionStatus(dealer=dealer_name, url=url or "")
        log_lines: List[str] = []

        async with async_playwright() as pw:
            if self.cloudflare_stealth:
                browser, context, page = await self.cloudflare_stealth.create_stealth_session(
                    pw,
                    headless=self.headless,
                )
            else:
                # Use existing browser manager
                browser, context = await self.browser_manager.open_context(pw, headless=self.headless)
                page = await self.browser_manager.create_enhanced_stealth_page(context)
            resolved_url = url
            resolution = None

            if resolver:
                normalized_homepage = homepage_url or (url and self._homepage_from_url(url))
                if not normalized_homepage:
                    raise ValueError("homepage_url is required when using contact resolver")
                resolution = await resolver.resolve(
                    context,
                    dealer_id=slug,
                    dealer_name=dealer_name,
                    homepage_url=normalized_homepage,
                    preferred_contact_url=url,
                )
                resolved_url = resolution.contact_url
                log_lines.append(
                    f"[info] Contact page resolved via {resolution.source}: {resolved_url}"
                )

            if not resolved_url:
                raise ValueError("Contact URL could not be determined")

            status.url = resolved_url
            if resolution:
                status.contact_resolution_source = resolution.source

            try:
                behavior_config = self.behavior_config
                if resolution and resolution.source in {"preferred", "cache"} and behavior_config.enable_warmup:
                    behavior_config = replace(behavior_config, enable_warmup=False)
                    log_lines.append("[human] Skipping warm-up navigation (direct contact URL)")

                log_lines.append(f"[info] Preparing contact page for {resolved_url}")

                if self.cloudflare_stealth:
                    # Use Cloudflare evasion navigation
                    log_lines.append("[info] Using Cloudflare evasion navigation")

                    direct_contact = False
                    if resolution:
                        direct_contact = resolution.source in {"preferred", "cache"}
                    elif url:
                        direct_contact = True

                    primary_nav = await self.cloudflare_stealth.navigate_with_cloudflare_evasion(
                        page,
                        resolved_url,
                        referrer=None,
                    )

                    nav_success = primary_nav
                    referrer_url = homepage_url if not direct_contact else None

                    if not primary_nav and referrer_url:
                        log_lines.append("[human] Retrying navigation via homepage warm-up")
                        nav_success = await self.cloudflare_stealth.navigate_with_cloudflare_evasion(
                            page,
                            resolved_url,
                            referrer=referrer_url,
                        )
                    if not nav_success:
                        log_lines.append("[error] Cloudflare evasion navigation failed")
                        status.status = "blocked"
                        status.errors.append("Cloudflare navigation failed")
                        return status
                    final_url = resolved_url
                else:
                    # Use existing navigation
                    final_url = await warm_up_and_navigate(page, resolved_url, log_lines, behavior_config)

                log_lines.append(f"[info] Contact page ready at {final_url}")

                # Handle cookie consent popups that may block form detection
                dismissed_consents = await self._handle_cookie_consent(page, log_lines)
                if dismissed_consents > 0:
                    log_lines.append(f"[info] Dismissed {dismissed_consents} cookie consent popup(s)")
                    # Wait a moment for page to settle after dismissing consents
                    await asyncio.sleep(1)

                if await self._is_blocked_page(page):
                    log_lines.append("[warn] Security block detected; aborting run")
                    blocked_path = artifact_dir / "blocked.png"
                    await page.screenshot(path=str(blocked_path), full_page=True)
                    status.status = "blocked"
                    status.errors.append("Encountered security block page")
                    status.artifacts["detected"] = str(blocked_path)
                    return status

                detection = await self.detector.detect_contact_form(page)

                detection_path = artifact_dir / "detected.png"
                await page.screenshot(path=str(detection_path), full_page=True)
                artifacts.detection = detection_path
                status.artifacts["detected"] = str(detection_path)

                if not detection.success:
                    status.status = "detection_failed"
                    status.errors.append("Form detection failed")
                    return status

                log_lines.append("[info] Form detected; beginning population")

                await self._populate_fields(page, detection, payload, status, log_lines)

                filled_path = artifact_dir / "filled.png"
                await page.screenshot(path=str(filled_path), full_page=True)
                artifacts.filled = filled_path
                status.artifacts["filled"] = str(filled_path)

                submission_ok = await self._submit_form(page, detection, status, log_lines)

                submitted_path = artifact_dir / "submitted.png"
                await page.screenshot(path=str(submitted_path), full_page=True)
                artifacts.submitted = submitted_path
                status.artifacts["submitted"] = str(submitted_path)

                status.status = "submission_success" if submission_ok else "submission_failed"

            except PlaywrightTimeoutError as exc:
                status.status = "timeout"
                status.errors.append(f"Timeout: {exc}")
            except Exception as exc:  # pylint: disable=broad-except
                status.status = "error"
                status.errors.append(str(exc))
            finally:
                await page.close()
                if self.cloudflare_stealth:
                    await self.cloudflare_stealth.close_session(browser, context)
                else:
                    await self.browser_manager.close_context(browser, context)

        log_path = artifact_dir / "run.log"
        log_path.write_text("\n".join(log_lines), encoding="utf-8")
        artifacts.log = log_path
        status.artifacts["log"] = str(log_path)

        summary_path = artifact_dir / "status.json"
        summary_path.write_text(status.to_json(), encoding="utf-8")
        status.artifacts["status"] = str(summary_path)

        return status

    def _homepage_from_url(self, url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
        except Exception:
            return None
        if not parsed.scheme or not parsed.netloc:
            return None
        return f"{parsed.scheme}://{parsed.netloc}/"

    async def _is_blocked_page(self, page: Page) -> bool:
        block_indicators = [
            "sorry, you have been blocked",
            "cloudflare ray id",
            "blocked because your browser",
            "request unsuccessful",
            "access denied",
            "why have i been blocked",
        ]
        body_text = (await page.inner_text("body")).lower()
        return any(indicator in body_text for indicator in block_indicators)

    async def _populate_fields(
        self,
        page: Page,
        detection: EnhancedFormResult,
        payload: ContactPayload,
        status: SubmissionStatus,
        log_lines: List[str],
    ) -> None:
        field_map = {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
            "zip": payload.zip_code,
            "message": payload.message,
        }

        for field_type, value in field_map.items():
            if not value:
                continue
            success = await self._fill_field(page, detection, field_type, value, log_lines)
            if success:
                status.fields_filled.append(field_type)
            else:
                status.missing_fields.append(field_type)

            # Human-like pause between fields
            if self.cloudflare_stealth:
                await asyncio.sleep(random.uniform(0.5, 1.5))

        phone_success = await self._fill_phone(page, detection, payload.phone, log_lines)
        if phone_success:
            status.fields_filled.append("phone")
        else:
            status.missing_fields.append("phone")

        dropdown_decisions = await self._handle_dropdowns(page, detection, log_lines)
        status.dropdown_choices.update(dropdown_decisions)

        checked_boxes = await self._handle_checkboxes(page, detection, log_lines)
        status.checkboxes_checked.extend(checked_boxes)

    async def _fill_field(
        self,
        page: Page,
        detection: EnhancedFormResult,
        field_type: str,
        value: str,
        log_lines: List[str],
    ) -> bool:
        field = detection.fields.get(field_type)
        if field:
            return await self._fill_by_selector(page, field.selector, value, log_lines, field_type)

        # fallback: find input by label text
        log_lines.append(f"[warn] {field_type} not in detection; attempting label search")
        selector = await self._find_input_by_label(page, field_type)
        if selector:
            return await self._fill_by_selector(page, selector, value, log_lines, field_type)
        log_lines.append(f"[error] Unable to find input for {field_type}")
        return False

    async def _is_honeypot_field(self, page: Page, selector: str) -> bool:
        """Runtime honeypot detection with comprehensive visibility checks."""
        try:
            is_honeypot = await page.evaluate("""
                (selector) => {
                    const element = document.querySelector(selector);
                    if (!element) return false; // If we can't find it, don't assume it's a trap

                    // Check if element is truly visible to users
                    const rect = element.getBoundingClientRect();
                    const styles = window.getComputedStyle(element);

                    // Hidden by CSS - these are strong indicators
                    if (styles.display === 'none' || styles.visibility === 'hidden') return true;
                    if (styles.opacity === '0' || styles.opacity === 0) return true;

                    // Position-based hiding - be more lenient with off-screen positioning
                    if (rect.width === 0 && rect.height === 0) return true;

                    // Only flag as honeypot if WAY off screen (not just slightly)
                    if (rect.left < -500 || rect.top < -500) return true;
                    if (rect.left > window.innerWidth + 500 || rect.top > window.innerHeight + 500) return true;

                    // Microscopic size (but allow small fields like mobile inputs)
                    if (rect.width < 2 && rect.height < 2) return true;

                    // Z-index behind other elements (more lenient)
                    if (parseInt(styles.zIndex) < -10) return true;

                    // Text indentation off-screen (classic honeypot technique)
                    if (parseInt(styles.textIndent) < -9999) return true;

                    // Check parent containers for hiding
                    let parent = element.parentElement;
                    while (parent && parent !== document.body) {
                        const parentStyles = window.getComputedStyle(parent);
                        if (parentStyles.display === 'none' || parentStyles.visibility === 'hidden') return true;
                        if (parentStyles.opacity === '0' || parentStyles.opacity === 0) return true;
                        parent = parent.parentElement;
                    }

                    // More conservative honeypot pattern checking
                    const name = (element.name || '').toLowerCase();
                    const id = (element.id || '').toLowerCase();
                    const className = (element.className || '').toLowerCase();
                    const placeholder = (element.placeholder || '').toLowerCase();

                    // Only flag if the field explicitly contains honeypot-specific terms
                    const explicitHoneypotPatterns = [
                        'honeypot', 'bot-trap', 'spam-check', 'robot-check',
                        'fake-field', 'decoy-field', 'anti-spam'
                    ];

                    if (explicitHoneypotPatterns.some(pattern =>
                        name.includes(pattern) || id.includes(pattern) ||
                        className.includes(pattern) || placeholder.includes(pattern)
                    )) return true;

                    // Check for suspicious instructions in placeholder or labels
                    const suspiciousInstructions = [
                        'leave this field blank', 'do not fill', 'ignore this field',
                        'for bots only', 'leave empty', 'do not enter'
                    ];

                    if (suspiciousInstructions.some(instruction =>
                        placeholder.includes(instruction)
                    )) return true;

                    // Check associated label for suspicious text
                    const labelElement = element.labels && element.labels[0];
                    if (labelElement) {
                        const labelText = (labelElement.textContent || '').toLowerCase();
                        if (suspiciousInstructions.some(instruction =>
                            labelText.includes(instruction)
                        )) return true;
                    }

                    return false;
                }
            """, selector)
            return is_honeypot
        except Exception:
            return False  # If we can't check, assume it's legitimate

    async def _fill_by_selector(
        self,
        page: Page,
        selector: str,
        value: str,
        log_lines: List[str],
        field_type: str,
    ) -> bool:
        try:
            # Runtime honeypot check before filling
            if await self._is_honeypot_field(page, selector):
                log_lines.append(f"[security] Skipping honeypot field: {field_type} ({selector})")
                return False

            locator = page.locator(selector)
            await locator.wait_for(timeout=4000)

            if self.cloudflare_stealth:
                log_lines.append(f"[info] Using advanced human-like filling for {field_type}")

                await locator.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.5, 1.2))

                # Multiple focus attempts mimicking human adjustments
                for _ in range(random.randint(1, 2)):
                    await locator.focus()
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                # Clear existing content via backspaces
                try:
                    current_value = await locator.input_value()
                except Exception:
                    current_value = ""

                if current_value:
                    await locator.focus()
                    for _ in range(len(current_value)):
                        await page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.03, 0.08))

                await asyncio.sleep(random.uniform(0.3, 0.8))

                # Natural typing cadence with occasional hesitations
                for index, char in enumerate(str(value)):
                    if random.random() < 0.08:
                        await asyncio.sleep(random.uniform(0.4, 0.9))

                    await locator.type(char)

                    if char.isspace():
                        delay = random.uniform(0.08, 0.15)
                    elif char.isdigit():
                        delay = random.uniform(0.05, 0.12)
                    elif index == 0:
                        delay = random.uniform(0.12, 0.2)
                    elif index == len(value) - 1:
                        delay = random.uniform(0.08, 0.15)
                    else:
                        delay = random.uniform(0.04, 0.1)

                    await asyncio.sleep(delay)

                await asyncio.sleep(random.uniform(0.2, 0.6))
                # Tab out to mimic human leaving the field
                await page.keyboard.press('Tab')
                await asyncio.sleep(random.uniform(0.3, 0.8))

            else:
                await locator.click()
                await locator.fill(value)

            log_lines.append(f"[info] Filled {field_type} via {selector}")
            return True
        except Exception as exc:  # pylint: disable=broad-except
            log_lines.append(f"[error] Failed to fill {field_type} via {selector}: {exc}")
            return False

    async def _find_input_by_label(self, page: Page, field_type: str) -> Optional[str]:
        label_keywords = {
            "first_name": ["first name", "given name"],
            "last_name": ["last name", "surname"],
            "email": ["email"],
            "zip": ["zip", "postal"],
            "message": ["message", "comments", "question"],
        }
        keywords = label_keywords.get(field_type, [])
        if not keywords:
            return None

        script = """
            (keywords) => {
                const entries = [];
                const labels = Array.from(document.querySelectorAll('label'));
                const escapeSelector = (value) => {
                    if (!value) return null;
                    if (window.CSS && window.CSS.escape) {
                        return CSS.escape(value);
                    }
                    return value.replace(/([ #.;?+*~'":!^$\\[\\]()=>|\\\\\\/])/g, '\\\\$1');
                };
                labels.forEach(label => {
                    const text = (label.textContent || '').toLowerCase();
                    if (!keywords.some(keyword => text.includes(keyword))) {
                        return;
                    }
                    let target = null;
                    const forAttr = label.getAttribute('for');
                    if (forAttr) {
                        const escaped = escapeSelector(forAttr);
                        if (escaped) {
                            target = document.querySelector(`#${escaped}`);
                        }
                    }
                    if (!target) {
                        const parent = label.closest('.gfield, .form-group, .field, div, li');
                        if (parent) {
                            target = parent.querySelector('input, textarea');
                        }
                    }
                    if (!target || target.type === 'hidden') {
                        return;
                    }
                    if (!target.id) {
                        target.id = `auto_field_${Math.random().toString(36).slice(2)}`;
                    }
                    entries.push(`#${target.id}`);
                });
                return entries;
            }
        """
        selectors = await page.evaluate(script, keywords)
        return selectors[0] if selectors else None

    async def _fill_phone(
        self,
        page: Page,
        detection: EnhancedFormResult,
        phone: str,
        log_lines: List[str],
    ) -> bool:
        digits = re.sub(r"\D", "", phone)
        if not digits:
            return False

        field = detection.fields.get("phone")
        if field:
            success = await self._fill_by_selector(page, field.selector, digits, log_lines, "phone")
            if success:
                return True

        # segmented phone inputs
        segment_selectors = await page.evaluate(
            """
            () => {
                const wrappers = Array.from(document.querySelectorAll('label, .gfield, .form-group, li'));
                const targets = [];
                wrappers.forEach(wrapper => {
                    const text = (wrapper.textContent || '').toLowerCase();
                    if (!text.includes('phone')) {
                        return;
                    }
                    const inputs = Array.from(wrapper.querySelectorAll('input[type="tel"], input[type="text"]'))
                        .filter(inp => inp.type !== 'hidden' && inp.offsetParent !== null && inp.value === '');
                    if (inputs.length >= 2 && inputs.length <= 4) {
                        const ids = inputs.map(inp => {
                            if (!inp.id) {
                                inp.id = `auto_phone_${Math.random().toString(36).slice(2)}`;
                            }
                            return `#${inp.id}`;
                        });
                        targets.push(ids);
                    }
                });
                return targets[0] || null;
            }
        """
        )

        if segment_selectors:
            segment_values = [digits[:3], digits[3:6], digits[6:]]
            for selector, value in zip(segment_selectors, segment_values):
                if not value:
                    continue
                await self._fill_by_selector(page, selector, value, log_lines, "phone_segment")
            return True

        log_lines.append("[warn] Unable to locate phone inputs")
        return False

    async def _handle_dropdowns(
        self,
        page: Page,
        detection: EnhancedFormResult,
        log_lines: List[str],
    ) -> Dict[str, str]:
        dropdowns: Dict[str, str] = {}
        select_entries = await self._collect_selects(detection, page)
        for entry in select_entries:
            choice = self._choose_dropdown_option(entry["label"], entry["options"])
            if not choice:
                continue
            try:
                selector = entry["selector"]
                await page.select_option(selector, label=choice)
                dropdowns[entry["label"] or entry["selector"]] = choice
                log_lines.append(f"[info] Selected '{choice}' for dropdown '{entry['label']}'")
            except Exception:
                # Attempt custom select fallback
                if await self._handle_custom_dropdown(page, entry["label"], choice):
                    dropdowns[entry["label"] or "custom"] = choice
                    log_lines.append(f"[info] Selected '{choice}' via custom dropdown handler")
                else:
                    log_lines.append(f"[warn] Could not select option for dropdown {entry['label']}")

        custom_results = await self._handle_custom_contact_dropdowns(page, log_lines)
        dropdowns.update(custom_results)
        return dropdowns

    async def _collect_selects(self, detection: EnhancedFormResult, page: Page) -> List[Dict[str, str]]:
        base = detection.form_element or page
        select_locator = base.locator("select")
        count = await select_locator.count()
        results: List[Dict[str, str]] = []

        for index in range(count):
            locator = select_locator.nth(index)
            try:
                element = await locator.element_handle()
                if element is None:
                    continue
                element_id = await element.get_attribute("id")
                name_attr = await element.get_attribute("name")

                label_text = ""
                escaped_id = None
                if element_id:
                    escaped_id = await locator.evaluate(
                        "el => (window.CSS && CSS.escape) ? CSS.escape(el.id) : el.id"
                    )
                    label_candidate = base.locator(f"label[for='{escaped_id}']").first
                    if await label_candidate.count() > 0:
                        try:
                            label_text = (await label_candidate.inner_text()).strip()
                        except Exception:
                            label_text = ""
                if not label_text:
                    wrapper = locator.locator(
                        "xpath=ancestor::*[contains(@class,'gfield') or contains(@class,'form-group') or contains(@class,'field')][1]"
                    )
                    if await wrapper.count() > 0:
                        inline_label = wrapper.locator("label").first
                        if await inline_label.count() > 0:
                            try:
                                label_text = (await inline_label.inner_text()).strip()
                            except Exception:
                                label_text = ""

                option_locator = locator.locator("option")
                option_count = await option_locator.count()
                options: List[str] = []
                for opt_index in range(option_count):
                    try:
                        text = (await option_locator.nth(opt_index).inner_text()).strip()
                        if text:
                            options.append(text)
                    except Exception:
                        continue

                selector = None
                if escaped_id:
                    selector = f"#{escaped_id}"
                elif name_attr:
                    selector = f"select[name='{name_attr}']"

                if selector:
                    results.append({
                        "label": label_text,
                        "options": options,
                        "selector": selector,
                    })
            except Exception:
                continue

        return results

    def _choose_dropdown_option(self, label: str, options: List[str]) -> Optional[str]:
        normalized_label = (label or "").lower()
        normalized_options = [opt.lower() for opt in options]
        if not options:
            return None
        contact_keywords = ["contact", "prefer", "reach", "method", "communicat", "respond"]
        if any(key in normalized_label for key in contact_keywords):
            for keyword in ["text", "sms", "message"]:
                for opt, norm in zip(options, normalized_options):
                    if keyword in norm:
                        return opt
            for keyword in ["phone", "call"]:
                for opt, norm in zip(options, normalized_options):
                    if keyword in norm:
                        return opt
            for keyword in ["email"]:
                for opt, norm in zip(options, normalized_options):
                    if keyword in norm:
                        return opt
            return options[0]
        reason_keywords = ["department", "reason", "interest", "topic", "type", "concern", "inquiry", "question"]
        if any(key in normalized_label for key in reason_keywords):
            for keyword in ["sales", "new", "vehicle", "lease", "inventory"]:
                for opt, norm in zip(options, normalized_options):
                    if keyword in norm:
                        return opt
            return options[0]
        if any("vehicle" in opt for opt in normalized_options):
            for opt, norm in zip(options, normalized_options):
                if "vehicle" in norm or "sales" in norm:
                    return opt
        return None

    async def _handle_custom_dropdown(self, page: Page, label: Optional[str], choice: str) -> bool:
        if not label:
            return False
        locator = page.locator(f"label:has-text('{label}')").first
        if await locator.count() == 0:
            return False
        try:
            wrapper = locator.locator("xpath=..")
            dropdown_toggle = wrapper.locator(".custom-select-dropdown").first
            if await dropdown_toggle.count() == 0:
                dropdown_toggle = locator.locator("xpath=../..//div[contains(@class,'dropdown')]")
            if await dropdown_toggle.count() == 0:
                return False
            await dropdown_toggle.click()
            await page.wait_for_timeout(300)
            option_locator = page.locator(f"text={choice}").first
            await option_locator.click()
            return True
        except Exception:
            return False

    async def _handle_custom_contact_dropdowns(self, page: Page, log_lines: List[str]) -> Dict[str, str]:
        """Handle bespoke dropdown implementations (ShiftDigital-style custom select)."""

        results: Dict[str, str] = {}
        container = page.locator(".preferred-contact").first
        if await container.count() == 0:
            return results

        toggle = container.locator(".custom-select-dropdown").first
        if await toggle.count() == 0:
            return results

        options = ["Phone", "Call", "Text", "SMS", "Email"]
        choice = None
        for keyword in options:
            choice = keyword
            if keyword in {"Phone", "Call"}:
                break

        try:
            await toggle.click()
            await page.wait_for_timeout(300)
            for keyword in options:
                locator = page.locator(f"text={keyword}").first
                if await locator.count() > 0:
                    await locator.click()
                    results["Preferred Contact Method"] = keyword
                    log_lines.append(f"[info] Custom dropdown set to {keyword}")
                    break
            if self.cloudflare_stealth:
                try:
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                except Exception:
                    pass
        except Exception as exc:
            log_lines.append(f"[warn] Custom dropdown selection failed: {exc}")

        return results

    async def _handle_checkboxes(
        self,
        page: Page,
        detection: EnhancedFormResult,
        log_lines: List[str],
    ) -> List[str]:
        script_form = """
            (form) => {
                const results = [];
                const boxes = Array.from(form.querySelectorAll('input[type="checkbox"]'));
                const esc = (value) => {
                    const escaper = window.CSS && window.CSS.escape ? window.CSS.escape : (val) => val.replace(/(['\"\\\\\\\\\\\s])/g, '\\\\$1');
                    return escaper(value);
                };
                boxes.forEach(box => {
                    if (box.disabled) return;
                    let labelText = '';
                    if (box.id) {
                        const lbl = form.querySelector(`label[for="${esc(box.id)}"]`);
                        if (lbl && lbl.textContent) {
                            labelText = lbl.textContent.trim();
                        }
                    }
                    if (!labelText) {
                        const parent = box.closest('.gfield, .form-group, label, div');
                        if (parent && parent.textContent) {
                            labelText = parent.textContent.trim();
                        }
                    }
                    if (!box.id) {
                        box.id = `auto_checkbox_${Math.random().toString(36).slice(2)}`;
                    }
                    results.push({ label: labelText, selector: `#${esc(box.id)}`, id: box.id });
                });
                return results;
            }
        """
        script_page = script_form.replace("(form) => {", "() => { const form = document;")
        if detection.form_element:
            try:
                checkboxes = await detection.form_element.evaluate(script_form)
            except Exception:
                checkboxes = await page.evaluate(script_page)
        else:
            checkboxes = await page.evaluate(script_page)
        checked = []
        relevant_keywords = [
            'agree', 'consent', 'privacy', 'terms', 'contact',
            'communication', 'accept', 'acknowledge', 'permission',
            'text', 'sms'
        ]

        for entry in checkboxes:
            try:
                label_text = (entry.get("label") or "").lower()
                locator = page.locator(entry["selector"]).first
                if await locator.count() == 0 or await locator.is_checked():
                    continue

                relevant = any(keyword in label_text for keyword in relevant_keywords)
                if not relevant and self.cloudflare_stealth:
                    continue

                await locator.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.8, 1.5))

                if self.cloudflare_stealth:
                    await locator.hover()
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                try:
                    await locator.check()
                except Exception:
                    label_selector = f"label[for='{entry.get('id', '')}']" if entry.get('id') else None
                    if label_selector:
                        label_loc = page.locator(label_selector).first
                        if await label_loc.count() > 0:
                            await label_loc.click()
                        else:
                            raise
                    else:
                        raise

                checked.append(entry["label"] or entry["selector"])
                log_lines.append(f"[info] Checked checkbox '{entry['label']}'")

                if self.cloudflare_stealth:
                    await asyncio.sleep(random.uniform(0.5, 1.2))

            except Exception as exc:
                try:
                    await page.locator(entry["selector"]).evaluate("el => el.checked = true")
                    checked.append(entry["label"] or entry["selector"])
                    log_lines.append(f"[info] Programmatically set checkbox '{entry['label']}'")
                except Exception:
                    log_lines.append(f"[warn] Failed to check checkbox {entry['selector']}: {exc}")
        custom_checked = await self._check_custom_checkbox_groups(page, log_lines)
        checked.extend(custom_checked)
        return checked

    async def _handle_cookie_consent(self, page: Page, log_lines: List[str]) -> int:
        """Handle cookie consent popups that block form detection."""
        dismissed_count = 0

        # Common cookie consent selectors
        cookie_consent_selectors = [
            # OneTrust (very common)
            '#onetrust-banner-sdk button[id*="accept"]',
            '#onetrust-banner-sdk button:has-text("Accept")',
            '#onetrust-banner-sdk button:has-text("Accept All")',
            '#onetrust-banner-sdk button:has-text("Confirm")',
            'button[id*="onetrust-accept"]',

            # Generic cookie banners
            '[class*="cookie"] button:has-text("Accept")',
            '[class*="cookie"] button:has-text("Agree")',
            '[class*="cookie"] button:has-text("OK")',
            '[class*="cookie"] button:has-text("Continue")',
            '[class*="consent"] button:has-text("Accept")',
            '[class*="consent"] button:has-text("Agree")',

            # Privacy/GDPR banners
            '[class*="privacy"] button:has-text("Accept")',
            '[class*="gdpr"] button:has-text("Accept")',

            # Common ID patterns
            '#cookie-accept', '#accept-cookies', '#cookieAccept',
            '#privacy-accept', '#consent-accept',

            # Close buttons for privacy banners
            '[class*="privacy"] button:has-text("✕")',
            '[class*="cookie"] button:has-text("✕")',
            '.privacy-banner .close', '.cookie-banner .close',
        ]

        for selector in cookie_consent_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    log_lines.append(f"[info] Found cookie consent: {selector}")
                    await element.click(timeout=5000)
                    dismissed_count += 1
                    log_lines.append(f"[info] Clicked cookie consent button")
                    # Brief pause between dismissals
                    await asyncio.sleep(0.5)
            except Exception:
                # Expected - most selectors won't match
                continue

        # Special handling for OneTrust overlay that might still be visible
        try:
            onetrust_overlay = page.locator('#onetrust-banner-sdk, .onetrust-pc-dark-filter')
            if await onetrust_overlay.is_visible(timeout=1000):
                # Try to hide it with JavaScript if clicking didn't work
                await page.evaluate("""
                    const overlays = document.querySelectorAll('#onetrust-banner-sdk, .onetrust-pc-dark-filter, [class*="onetrust"]');
                    overlays.forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.remove();
                    });
                """)
                log_lines.append("[info] Force-hidden OneTrust overlay")
                dismissed_count += 1
        except Exception:
            pass

        return dismissed_count

    async def _dismiss_overlays(self, page: Page, log_lines: List[str]) -> int:
        """Dismiss overlays and popups that might block form submission."""
        overlays_dismissed = 0

        # Comprehensive overlay selectors
        overlay_selectors = [
            # Engagement/marketing overlays (like the one blocking submit)
            '#engagement-container-119829',
            '#layer-cover-119829',
            '#largeLayoutHeader[contenteditable="false"]',

            # Feedback/survey popups
            '[class*="feedback"] button:has-text("No thanks")',
            '[class*="feedback"] button:has-text("×")',
            '[class*="feedback"] .close',
            'button:has-text("No thanks")',
            '.no-thanks',

            # Emplifi/survey widgets
            '[class*="emplifi"] button',
            '[class*="survey"] button:has-text("No")',
            '[class*="survey"] .close',

            # Chat widgets
            '[class*="chat"] .close',
            '[class*="chat"] .minimize',
            '[id*="chat"] .close',
            '.chat-widget .close',

            # Marketing popups
            '.popup .close',
            '.modal .close',
            '.overlay .close',
            '[class*="popup"] button[aria-label="Close"]',

            # Cookie banners
            '[class*="cookie"] button:has-text("Accept")',
            '[class*="cookie"] button:has-text("OK")',

            # Generic close buttons
            'button[aria-label="Close"]',
            'button[title="Close"]',
            '.close-button',
            '.btn-close',
            '[data-dismiss]'
        ]

        for selector in overlay_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0:
                    try:
                        if await locator.is_visible():
                            await locator.click(timeout=2000)
                            overlays_dismissed += 1
                            log_lines.append(f"[info] Dismissed overlay: {selector}")
                            await asyncio.sleep(0.5)
                    except Exception:
                        # Try to remove via JavaScript if click fails
                        try:
                            await page.evaluate(f"document.querySelector('{selector}')?.remove()")
                            overlays_dismissed += 1
                            log_lines.append(f"[info] Removed overlay via JS: {selector}")
                        except Exception:
                            continue
            except Exception:
                continue

        # Press Escape key to dismiss modal overlays
        try:
            await page.keyboard.press('Escape')
            await asyncio.sleep(0.5)
            log_lines.append("[info] Pressed Escape to dismiss modals")
        except Exception:
            pass

        # Hide engagement containers and sticky elements specifically
        try:
            await page.evaluate("""
                () => {
                    const engagementContainers = document.querySelectorAll('[id*="engagement"], [class*="engagement"]');
                    engagementContainers.forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.opacity = '0';
                        el.style.pointerEvents = 'none';
                    });

                    // Hide sticky action bars and floating elements
                    const stickyElements = document.querySelectorAll('#actionbar, [data-widget*="action-bar"], .di-action-bar, .di-stacks');
                    stickyElements.forEach(el => {
                        el.style.display = 'none';
                        el.style.pointerEvents = 'none';
                    });

                    // Hide elements with data-radar (analytics/tracking overlays)
                    const radarElements = document.querySelectorAll('[data-radar]');
                    radarElements.forEach(el => {
                        if (el.style.position === 'fixed' || el.style.position === 'absolute') {
                            el.style.display = 'none';
                            el.style.pointerEvents = 'none';
                        }
                    });

                    // Also hide common overlay patterns
                    const overlaySelectors = ['[id*="layer-cover"]', '[class*="modal-backdrop"]', '[class*="overlay"]'];
                    overlaySelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            el.style.display = 'none';
                        });
                    });
                }
            """)
            log_lines.append("[info] Hidden engagement containers and sticky elements via JavaScript")
        except Exception:
            pass

        log_lines.append(f"[info] Dismissed {overlays_dismissed} overlays")
        return overlays_dismissed

    async def _check_custom_checkbox_groups(self, page: Page, log_lines: List[str]) -> List[str]:
        labels: List[str] = []
        containers = page.locator("div[class*='custom-checkbox']")
        count = await containers.count()
        for index in range(count):
            container = containers.nth(index)
            try:
                label_text = (await container.inner_text()).strip()
            except Exception:
                label_text = "(custom checkbox)"
            try:
                clickable = container.locator("input[type='checkbox']").first
                if await clickable.count() > 0:
                    if not await clickable.is_checked():
                        try:
                            await clickable.click()
                        except Exception:
                            await container.click()
                    labels.append(label_text)
                    log_lines.append(f"[info] Checked custom checkbox '{label_text}'")
            except Exception:
                continue
        return labels

    async def _submit_form(
        self,
        page: Page,
        detection: EnhancedFormResult,
        status: SubmissionStatus,
        log_lines: List[str],
    ) -> bool:
        submit_locator = detection.submit_button or (detection.form_element or page).locator("button[type='submit'], input[type='submit']").first
        click_performed = False
        try:
            if self.cloudflare_stealth:
                log_lines.append("[info] Using enhanced anti-detection submission protocol")

                # Phase 1: Enhanced form review with variable patterns
                review_pattern = random.choice(['quick', 'thorough', 'nervous'])
                log_lines.append(f"[info] Using '{review_pattern}' review pattern")

                if review_pattern == 'quick':
                    # Quick but confident user
                    await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                    await asyncio.sleep(random.uniform(1.0, 2.0))
                    await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
                    await asyncio.sleep(random.uniform(1.5, 2.5))

                elif review_pattern == 'thorough':
                    # Careful, methodical user
                    await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                    await asyncio.sleep(random.uniform(2.5, 4.0))

                    form_height = await page.evaluate("document.body.scrollHeight")
                    scroll_steps = random.randint(4, 7)
                    for step in range(scroll_steps):
                        scroll_position = (form_height // scroll_steps) * (step + 1)
                        await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
                        await asyncio.sleep(random.uniform(2.0, 3.5))

                        # Occasional page interactions during review
                        if random.random() < 0.3:
                            viewport = page.viewport_size
                            x = random.randint(200, viewport['width'] - 200)
                            y = random.randint(200, viewport['height'] - 200)
                            await page.mouse.move(x, y)
                            await asyncio.sleep(random.uniform(0.5, 1.0))

                else:  # nervous
                    # Indecisive user with multiple scrolls
                    for _ in range(random.randint(2, 4)):
                        direction = random.choice(['up', 'down'])
                        if direction == 'up':
                            await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                        else:
                            await page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
                        await asyncio.sleep(random.uniform(1.0, 2.5))

                # Phase 2: Dismiss overlays before submit interaction
                log_lines.append("[info] Dismissing overlays before submission")
                await self._dismiss_overlays(page, log_lines)

                # Phase 2: Submit button interaction with randomized approach
                await submit_locator.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.8, 1.8))

                interaction_style = random.choice(['direct', 'hesitant', 'precise'])
                log_lines.append(f"[info] Using '{interaction_style}' interaction style")

                if interaction_style == 'direct':
                    # Direct approach - hover and click
                    await submit_locator.hover()
                    await asyncio.sleep(random.uniform(0.5, 1.2))

                elif interaction_style == 'hesitant':
                    # Multiple hover attempts (indecision)
                    for _ in range(random.randint(2, 5)):
                        await submit_locator.hover()
                        await asyncio.sleep(random.uniform(0.6, 1.4))

                        # Move away occasionally
                        if random.random() < 0.4:
                            box = await submit_locator.bounding_box()
                            if box:
                                away_x = box['x'] + random.randint(-80, 80)
                                away_y = box['y'] + random.randint(-40, 40)
                                await page.mouse.move(away_x, away_y)
                                await asyncio.sleep(random.uniform(0.3, 0.8))

                    await submit_locator.hover()
                    await asyncio.sleep(random.uniform(0.8, 1.6))

                else:  # precise
                    # Careful positioning
                    box = await submit_locator.bounding_box()
                    if box:
                        center_x = box['x'] + box['width'] / 2
                        center_y = box['y'] + box['height'] / 2
                        await page.mouse.move(center_x, center_y)
                        await asyncio.sleep(random.uniform(0.4, 0.9))

                # Phase 3: Variable hesitation patterns
                hesitation_type = random.choice(['short', 'medium', 'long', 'variable'])

                if hesitation_type == 'short':
                    hesitation = random.uniform(1.5, 3.0)
                elif hesitation_type == 'medium':
                    hesitation = random.uniform(3.0, 6.0)
                elif hesitation_type == 'long':
                    hesitation = random.uniform(6.0, 12.0)
                else:  # variable - multiple short hesitations
                    total_hesitation = 0
                    for _ in range(random.randint(2, 4)):
                        pause = random.uniform(0.8, 2.5)
                        await asyncio.sleep(pause)
                        total_hesitation += pause
                        # Micro mouse movements during hesitation
                        if random.random() < 0.5:
                            current_x, current_y = await page.evaluate("() => [window.mouseX || 0, window.mouseY || 0]")
                            new_x = current_x + random.randint(-5, 5)
                            new_y = current_y + random.randint(-5, 5)
                            await page.mouse.move(new_x, new_y)
                    hesitation = total_hesitation

                if hesitation_type != 'variable':
                    log_lines.append(f"[info] {hesitation_type} hesitation for {hesitation:.1f}s")
                    await asyncio.sleep(hesitation)
                else:
                    log_lines.append(f"[info] Variable hesitation pattern completed ({total_hesitation:.1f}s total)")

                try:
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    await submit_locator.click(timeout=8000)
                    log_lines.append("[info] Submit clicked (natural)")
                    click_performed = True
                except Exception as exc:
                    log_lines.append(f"[warn] Natural click failed: {exc}")
                    try:
                        await asyncio.sleep(2)
                        await submit_locator.click(force=True, timeout=8000)
                        log_lines.append("[info] Submit clicked (force)")
                        click_performed = True
                    except Exception as exc_force:
                        log_lines.append(f"[warn] Force click failed: {exc_force}")
                        await asyncio.sleep(2)
                        try:
                            await page.evaluate(
                                """
                                    () => {
                                        const button = document.querySelector('button[type="submit"], input[type="submit"]');
                                        if (button) {
                                            const events = ['mousedown', 'mouseup', 'click'];
                                            events.forEach(eventType => {
                                                const event = new MouseEvent(eventType, {
                                                    bubbles: true,
                                                    cancelable: true,
                                                    view: window,
                                                });
                                                button.dispatchEvent(event);
                                            });
                                            const form = button.closest('form');
                                            if (form) {
                                                form.submit();
                                                return true;
                                            }
                                        }
                                        return false;
                                    }
                                """
                            )
                            log_lines.append("[info] Submit triggered via JavaScript fallback")
                            click_performed = True
                        except Exception as exc_js:
                            log_lines.append(f"[error] JavaScript submission failed: {exc_js}")
            else:
                await submit_locator.click()
                log_lines.append("[info] Submit button clicked")
                click_performed = True
        except Exception as exc:
            log_lines.append(f"[error] Failed to click submit: {exc}")
            status.errors.append("Submit click failed")
            return False

        if not click_performed:
            status.errors.append("Submit click failed")
            return False

        success_patterns = [
            "thank you",
            "we will be in touch",
            "submission received",
            "successfully sent",
            "we have received",
            "your message has been sent",
        ]
        error_selectors = [
            ".validation_error",
            ".gform_validation_errors",
            ".error-message",
            ".form-error",
            "[role='alert']",
            ".alert-danger",
            ".field-error"
        ]
        try:
            await page.wait_for_timeout(1500)
            confirmation_selector = "div.gform_confirmation_message, .alert-success, [role='alert'], .form-confirmation"
            locator = page.locator(confirmation_selector).first
            if await locator.count() > 0:
                text = (await locator.inner_text()).strip()
                if text:
                    status.confirmation_text = text
                log_lines.append(f"[info] Submission confirmation detected via selector: {text[:80]}")
                await asyncio.sleep(5)
                return True
        except Exception:
            pass

        try:
            # check for validation errors before inspecting entire DOM
            for selector in error_selectors:
                error_locator = page.locator(selector).first
                if await error_locator.count() > 0:
                    try:
                        text = (await error_locator.inner_text()).strip()
                    except Exception:
                        text = selector
                    status.errors.append(text)
                    log_lines.append(f"[warn] Validation error detected: {text[:120]}")
                    return False

            content = (await page.content()).lower()
            for pattern in success_patterns:
                if pattern in content:
                    status.confirmation_text = pattern
                    log_lines.append(f"[info] Submission confirmation detected: {pattern}")
                    await asyncio.sleep(5)
                    return True
        except Exception:
            pass

        # final attempt to capture error messages inline
        try:
            error_texts = await page.evaluate("""
                () => Array.from(document.querySelectorAll('.gfield_error, .validation_error, .error-message')).map(node => node.textContent.trim()).filter(Boolean)
            """)
            for text in error_texts or []:
                status.errors.append(text)
                log_lines.append(f"[warn] Inline validation error: {text[:120]}")
        except Exception:
            pass

        log_lines.append("[warn] No confirmation text detected; treating as failure")
        status.errors.append("No confirmation detected")
        return False


DEFAULT_PLACEHOLDER = ContactPayload(
    first_name="Miguel",
    last_name="Montoya",
    email="migueljmontoya@protonmail.com",
    phone="6503320719",
    zip_code="90066",
    message="Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel",
)
