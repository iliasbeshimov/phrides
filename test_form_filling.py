#!/usr/bin/env python3
"""
Test the complete form filling pipeline with Cloudflare evasion.
This will test the full flow: navigate -> detect form -> fill -> submit.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.browser.cloudflare_stealth_config import CloudflareStealth
from src.automation.forms.stealth_form_detector import StealthFormDetector
from src.automation.forms.human_form_filler import HumanFormFiller


async def test_complete_pipeline():
    """Test the complete form filling pipeline with stealth techniques."""
    print("🎯 COMPLETE FORM FILLING PIPELINE TEST")
    print("=" * 60)

    test_url = "https://www.capcitycdjr.com/contact-us/"
    test_data = {
        'first_name': 'Miguel',
        'last_name': 'Montoya',
        'email': 'migueljmontoya@protonmail.com',
        'phone': '650-688-2311',
        'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available? Best, Miguel'
    }

    print(f"🔍 Testing URL: {test_url}")
    print("⚠️  BROWSER WILL OPEN - WATCH THE COMPLETE AUTOMATION")
    print("=" * 60)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        # Stage 1: Setup
        print("\n🚀 Stage 1: Setting up stealth browser...")
        start_time = time.time()
        browser, context, page = await stealth.create_stealth_session()
        setup_time = time.time() - start_time
        print(f"   ✅ Browser ready ({setup_time:.2f}s)")

        # Stage 2: Navigate
        print("\n🌐 Stage 2: Navigating with Cloudflare evasion...")
        nav_start = time.time()
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, test_url)
        nav_time = time.time() - nav_start
        print(f"   🕒 Navigation time: {nav_time:.2f}s")

        if not nav_success:
            print("   ❌ Navigation failed - Cloudflare blocked")
            return

        print("   ✅ Navigation successful - Cloudflare bypassed!")

        # Stage 3: Form Detection
        print("\n📝 Stage 3: Detecting form with stealth approach...")
        detection_start = time.time()
        detector = StealthFormDetector()
        form_result = await detector.detect_form_quickly(page)
        detection_time = time.time() - detection_start
        print(f"   🕒 Detection time: {detection_time:.2f}s")

        if not form_result.success:
            print(f"   ❌ Form detection failed: {form_result.detection_method}")
            return

        print(f"   ✅ Form detected! Method: {form_result.detection_method}")
        print(f"   📋 Fields found: {list(form_result.fields.keys())}")

        # Stage 4: Human-like Form Filling
        print("\n✍️  Stage 4: Filling form with human-like behavior...")
        filling_start = time.time()
        human_filler = HumanFormFiller()
        filled_fields = []

        for field_name, field_info in form_result.fields.items():
            if field_name in test_data:
                print(f"   📝 Filling {field_name}...")
                success = await human_filler.fill_field_naturally(
                    page,
                    field_info.selector,
                    test_data[field_name],
                    field_name
                )
                if success:
                    filled_fields.append(field_name)
                    print(f"      ✅ {field_name} filled successfully")
                else:
                    print(f"      ❌ {field_name} failed to fill")

                # Natural pause between fields
                await human_filler.pause_between_fields(field_name)

        filling_time = time.time() - filling_start
        print(f"   🕒 Form filling time: {filling_time:.2f}s")
        print(f"   📊 Fields filled: {len(filled_fields)}/{len(form_result.fields)}")

        # Stage 5: Screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"complete_pipeline_test_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"   📸 Screenshot saved: {screenshot_path}")

        # Stage 6: Optional Submission
        if form_result.submit_selector and filled_fields:
            submit_choice = input("\n🤔 Submit the form? (y/N): ").lower().startswith('y')
            if submit_choice:
                print("\n📤 Stage 6: Submitting form...")
                submit_start = time.time()
                submit_button = page.locator(form_result.submit_selector).first
                await submit_button.click()
                submit_time = time.time() - submit_start
                print(f"   ✅ Form submitted ({submit_time:.2f}s)")

                # Wait for response
                await asyncio.sleep(3)
                post_submit_screenshot = f"form_submitted_{timestamp}.png"
                await page.screenshot(path=post_submit_screenshot, full_page=True)
                print(f"   📸 Post-submission screenshot: {post_submit_screenshot}")
            else:
                print("   ⏭️  Skipping submission (testing only)")

        total_time = time.time() - start_time
        print(f"\n⏱️  Total pipeline time: {total_time:.2f}s")

        # Final Results
        print("\n🎉 PIPELINE TEST COMPLETED!")
        print("📊 Results Summary:")
        print(f"   ✅ Cloudflare evasion: SUCCESS")
        print(f"   ✅ Form detection: SUCCESS")
        print(f"   ✅ Form filling: {len(filled_fields)}/{len(form_result.fields)} fields")
        print(f"   📸 Screenshots: {screenshot_path}")

        # Keep browser open for inspection
        print("\n⏳ Keeping browser open for 10 seconds for inspection...")
        await asyncio.sleep(10)

    except Exception as exc:
        print(f"\n💥 Pipeline test failed: {exc}")

    finally:
        print("\n🧹 Cleaning up...")
        await stealth.close_session(browser, context)


if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())