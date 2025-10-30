"""Generate an initial label file by running the detector against a live page."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector

FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "form_detection"
INDEX_PATH = FIXTURE_ROOT / "dataset_index.json"
LABEL_DIR = FIXTURE_ROOT / "labels"


def load_index() -> Dict[str, Dict]:
    data = json.loads(INDEX_PATH.read_text())
    return {entry["slug"]: entry for entry in data.get("entries", [])}


def default_field_spec(selector: str) -> Dict[str, object]:
    return {
        "selectors": [selector],
        "label_text": [],
        "input_type": None,
        "required": True,
    }


async def capture_live(detector: EnhancedFormDetector, slug: str, url: str) -> Dict[str, object]:
    manager = EnhancedStealthBrowserManager()
    async with async_playwright() as playwright_instance:
        browser, context = await manager.open_context(playwright_instance)
        page = await manager.create_enhanced_stealth_page(context)
        result = None

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_load_state("networkidle", timeout=60000)
            except PlaywrightTimeoutError:
                pass

            result = await detector.detect_contact_form(page)
        finally:
            await page.close()
            await manager.close_context(browser, context)

    if result is None:
        raise RuntimeError("Form detection did not complete")

    fields: Dict[str, object] = {}
    for field, info in result.fields.items():
        spec = default_field_spec(info.selector)
        if field == "phone":
            spec.update({"format": "unknown", "segments": []})
        fields[field] = spec

    slug_dir = FIXTURE_ROOT / "pages" / slug
    label = {
        "dealer_slug": slug,
        "contact_url": url,
        "platform_hint": None,
        "snapshot_path": str((slug_dir / "contact.html").relative_to(ROOT)),
        "screenshot_path": str((FIXTURE_ROOT / "screenshots" / f"{slug}.png").relative_to(ROOT)),
        "last_verified_at": datetime.now(timezone.utc).isoformat(),
        "expected_fields": fields,
        "form_metadata": {
            "form_selector": "",
            "submit_selector": "",
            "notes": "Populate selectors, labels, and optional fields before validating."
        }
    }
    return label


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a label JSON from live detection")
    parser.add_argument("slug", help="Dealer slug listed in dataset_index.json")
    parser.add_argument("--url", help="Override URL instead of using the index")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing label")
    return parser.parse_args()


async def main_async() -> None:
    args = parse_args()
    index = load_index()
    entry = index.get(args.slug)
    if not entry:
        raise SystemExit(f"Slug '{args.slug}' not found in dataset index")

    label_path = LABEL_DIR / f"{args.slug}.json"
    if label_path.exists() and not args.overwrite:
        raise SystemExit(f"Label already exists at {label_path}. Use --overwrite to replace it.")

    detector = EnhancedFormDetector()
    url = args.url or entry["contact_url"]
    label = await capture_live(detector, args.slug, url)
    LABEL_DIR.mkdir(parents=True, exist_ok=True)
    label_path.write_text(json.dumps(label, indent=2))
    print(f"Bootstrap label written to {label_path}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
