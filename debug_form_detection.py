#!/usr/bin/env python3
"""
Debug form detection to see what fields are actually found.
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

from src.automation.browser.cloudflare_stealth_config import CloudflareStealth
from src.automation.forms.stealth_form_detector import StealthFormDetector


async def debug_form_detection():
    """Debug what fields are actually found."""
    print("🔍 DEBUGGING FORM DETECTION")
    print("=" * 50)

    test_url = "https://www.capcitycdjr.com/contact-us/"
    stealth = CloudflareStealth()

    try:
        browser, context, page = await stealth.create_stealth_session()

        print(f"Navigating to: {test_url}")
        await stealth.navigate_with_cloudflare_evasion(page, test_url)

        detector = StealthFormDetector()

        # Manual form detection with debugging
        print("\n📝 Finding form...")
        form_locator = await detector._find_form_quickly(page)
        if not form_locator:
            print("❌ No form found")
            return

        print("✅ Form found!")

        print("\n🔍 Detecting fields manually...")
        fields = await detector._detect_fields_quickly(form_locator)

        print(f"\n📋 Fields found: {len(fields)}")
        for field_type, field_info in fields.items():
            print(f"   - {field_type}: {field_info.selector} (confidence: {field_info.confidence})")

        # Check our contact field logic
        contact_fields = ['email', 'phone', 'first_name', 'last_name', 'message']
        has_contact_field = any(field_type in fields for field_type in contact_fields)
        print(f"\n🎯 Has contact field: {has_contact_field}")
        print(f"   Contact fields found: {[f for f in contact_fields if f in fields]}")

        await page.screenshot(path="debug_form_detection.png", full_page=True)
        print("📸 Screenshot saved: debug_form_detection.png")

    finally:
        await stealth.close_session(browser, context)


if __name__ == "__main__":
    asyncio.run(debug_form_detection())