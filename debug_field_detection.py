#!/usr/bin/env python3
"""
Debug Field Detection - Analyze what fields exist on failed sites
"""

import asyncio
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from playwright.async_api import async_playwright

async def analyze_form_fields(url):
    """Analyze all form fields on a page."""
    print(f"🔍 ANALYZING FORM FIELDS: {url}")
    print("=" * 60)

    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(url, timeout=15000)
        await asyncio.sleep(3)

        # Get all input and textarea elements
        all_inputs = await page.locator('input, textarea, select').all()

        print(f"📊 Found {len(all_inputs)} form elements:")
        print("-" * 40)

        for i, element in enumerate(all_inputs, 1):
            try:
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                input_type = await element.get_attribute('type') or 'text'
                name = await element.get_attribute('name') or ''
                id_attr = await element.get_attribute('id') or ''
                placeholder = await element.get_attribute('placeholder') or ''
                aria_label = await element.get_attribute('aria-label') or ''

                # Check visibility
                is_visible = await element.is_visible()
                bounding_box = await element.bounding_box()

                print(f"{i:2d}. {tag_name}[type='{input_type}'] - {'VISIBLE' if is_visible else 'HIDDEN'}")
                if name:
                    print(f"    name: {name}")
                if id_attr:
                    print(f"    id: {id_attr}")
                if placeholder:
                    print(f"    placeholder: {placeholder}")
                if aria_label:
                    print(f"    aria-label: {aria_label}")
                if bounding_box:
                    print(f"    size: {bounding_box['width']}x{bounding_box['height']}")
                print()

            except Exception as e:
                print(f"{i:2d}. ERROR analyzing element: {e}")

    except Exception as e:
        print(f"❌ Error loading page: {e}")

    finally:
        await browser.close()
        await playwright.stop()

async def main():
    """Debug field detection on failed sites."""

    # Test the sites that failed
    failed_sites = [
        "https://www.lithiachrysleranchorage.com/inquiry/",
        "https://www.anchoragechryslercenter.com"
    ]

    for url in failed_sites:
        await analyze_form_fields(url)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())