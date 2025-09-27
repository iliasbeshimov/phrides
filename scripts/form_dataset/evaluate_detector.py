"""Run enhanced form detection against saved fixtures and report accuracy metrics."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.automation.forms.enhanced_form_detector import EnhancedFormDetector

FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "form_detection"
INDEX_PATH = FIXTURE_ROOT / "dataset_index.json"
LABEL_DIR = FIXTURE_ROOT / "labels"


@dataclass
class DealerReport:
    slug: str
    dealer_name: str
    expected_fields: List[str]
    detected_fields: List[str]
    missing_fields: List[str]
    extra_fields: List[str]
    selector_matches: int
    selector_total: int
    success: bool
    details: Dict[str, Dict[str, str]]


def load_index() -> Dict[str, Dict]:
    data = json.loads(INDEX_PATH.read_text())
    return {entry["slug"]: entry for entry in data.get("entries", [])}


def load_label(slug: str) -> Optional[Dict]:
    label_path = LABEL_DIR / f"{slug}.json"
    if not label_path.exists():
        return None
    return json.loads(label_path.read_text())


def field_selector_match(expected_selectors: Iterable[str], detected_selector: str) -> bool:
    normalized = {sel.strip() for sel in expected_selectors}
    return detected_selector.strip() in normalized


async def evaluate_slug(detector: EnhancedFormDetector, slug: str, dealer_meta: Dict) -> DealerReport:
    label = load_label(slug)
    if not label:
        raise FileNotFoundError(f"Label missing for slug '{slug}'. Create {LABEL_DIR / f'{slug}.json'}")

    html_path = ROOT / label["snapshot_path"]
    if not html_path.exists():
        raise FileNotFoundError(f"Snapshot missing for slug '{slug}': {html_path}")

    uri = html_path.resolve().as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(uri, wait_until="load")
        result = await detector.detect_contact_form(page)
        await browser.close()

    expected_fields = list(label.get("expected_fields", {}).keys())
    detected_fields = list(result.fields.keys())

    missing_fields = [field for field in expected_fields if field not in result.fields]
    extra_fields = [field for field in detected_fields if field not in expected_fields]

    selector_matches = 0
    selector_total = 0
    details: Dict[str, Dict[str, str]] = {}

    for field, spec in label.get("expected_fields", {}).items():
        selectors = spec.get("selectors", [])
        if not selectors:
            continue
        selector_total += 1
        detected = result.fields.get(field)
        if detected and field_selector_match(selectors, detected.selector):
            selector_matches += 1
            details[field] = {
                "status": "match",
                "selector": detected.selector
            }
        elif detected:
            details[field] = {
                "status": "mismatch",
                "expected": ", ".join(selectors),
                "actual": detected.selector
            }
        else:
            details[field] = {
                "status": "missing",
                "expected": ", ".join(selectors)
            }

    success = not missing_fields and selector_matches == selector_total

    return DealerReport(
        slug=slug,
        dealer_name=dealer_meta.get("dealer_name", slug),
        expected_fields=expected_fields,
        detected_fields=detected_fields,
        missing_fields=missing_fields,
        extra_fields=extra_fields,
        selector_matches=selector_matches,
        selector_total=selector_total,
        success=success,
        details=details,
    )


async def run(slugs: Optional[List[str]]) -> Tuple[List[DealerReport], Dict[str, int]]:
    index = load_index()
    detector = EnhancedFormDetector()
    results: List[DealerReport] = []

    target_slugs = slugs or list(index.keys())

    successes = failures = 0

    for slug in target_slugs:
        meta = index.get(slug)
        if not meta:
            raise SystemExit(f"Slug '{slug}' not found in dataset index")
        try:
            report = await evaluate_slug(detector, slug, meta)
            results.append(report)
            if report.success:
                successes += 1
            else:
                failures += 1
        except FileNotFoundError as exc:
            print(f"[WARN] {exc}")
            failures += 1

    summary = {"successes": successes, "failures": failures, "total": successes + failures}
    return results, summary


def print_report(reports: List[DealerReport], summary: Dict[str, int]) -> None:
    for report in reports:
        status = "PASS" if report.success else "FAIL"
        print(f"== {status}: {report.dealer_name} ({report.slug})")
        print(f"   expected: {report.expected_fields}")
        print(f"   detected: {report.detected_fields}")
        if report.missing_fields:
            print(f"   missing: {report.missing_fields}")
        if report.extra_fields:
            print(f"   extra: {report.extra_fields}")
        print(f"   selector matches: {report.selector_matches}/{report.selector_total}")
        for field, detail in report.details.items():
            status = detail.get("status", "")
            if status == "match":
                print(f"     - {field}: matched {detail['selector']}")
            elif status == "mismatch":
                print(f"     - {field}: mismatch\n         expected: {detail['expected']}\n         actual:   {detail['actual']}")
            else:
                print(f"     - {field}: missing; expected {detail['expected']}")
        print()

    print("== Summary ==")
    print(json.dumps(summary, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate enhanced form detector against fixtures")
    parser.add_argument("slug", nargs="*", help="Optional subset of slugs to evaluate")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports, summary = asyncio.run(run(args.slug or None))
    print_report(reports, summary)


if __name__ == "__main__":
    main()
