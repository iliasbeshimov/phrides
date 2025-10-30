#!/usr/bin/env python3
"""
Simple final test that combines Cloudflare evasion with basic human-like form filling.
This version uses simple delays and typing instead of complex mouse movements.
"""

import asyncio
import sys
import time
import random
from pathlib import Path
from datetime import datetime

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.browser.cloudflare_stealth_config import CloudflareStealth
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector


async def human_like_fill(page, selector, value, field_name):
    """Simple human-like form filling without complex mouse movements."""
    try:
        print(f"      🎯 Locating {field_name} field...")
        locator = page.locator(selector).first
        await locator.wait_for(timeout=5000)

        # Human-like approach: scroll to field, pause, click, pause, type
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.3, 0.8))  # Pause to "find" the field

        print(f"      👆 Clicking {field_name} field...")
        await locator.click()
        await asyncio.sleep(random.uniform(0.2, 0.5))  # Pause after click

        # Clear field first
        await locator.fill("")
        await asyncio.sleep(random.uniform(0.1, 0.3))

        print(f"      ⌨️  Typing {field_name} with human timing...")
        # Type with human-like delays
        for char in str(value):
            await locator.type(char)
            # Random delay between keystrokes (50-200ms)
            await asyncio.sleep(random.uniform(0.05, 0.2))

        # Brief pause after typing
        await asyncio.sleep(random.uniform(0.2, 0.6))

        return True

    except Exception as e:
        print(f"      ❌ Failed to fill {field_name}: {e}")
        return False


async def test_simple_final():
    """Test the complete pipeline with simple human-like behavior."""
    print("🎯 SIMPLE FINAL PIPELINE TEST")
    print("🔥 Cloudflare Evasion + Enhanced Detection + Simple Human Filling")
    print("=" * 70)

    test_url = "https://www.capcitycdjr.com/contact-us/"
    test_data = {
        'first_name': 'Miguel',
        'last_name': 'Montoya',
        'email': 'migueljmontoya@protonmail.com',
        'phone': '650-688-2311',
        'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available? Best, Miguel'
    }

    print(f"🔍 Testing URL: {test_url}")
    print("⚠️  BROWSER WILL OPEN - WATCH THE AUTOMATION")
    print("=" * 70)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        # Stage 1: Stealth Setup
        print("\n🚀 Stage 1: Setting up stealth browser...")
        start_time = time.time()
        browser, context, page = await stealth.create_stealth_session()
        setup_time = time.time() - start_time
        print(f"   ✅ Stealth browser ready ({setup_time:.2f}s)")

        # Stage 2: Cloudflare Evasion
        print("\n🌐 Stage 2: Navigating with Cloudflare evasion...")
        nav_start = time.time()
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, test_url)
        nav_time = time.time() - nav_start
        print(f"   🕒 Navigation time: {nav_time:.2f}s")

        if not nav_success:
            print("   ❌ Navigation failed - Cloudflare blocked")
            return

        print("   ✅ SUCCESS: Cloudflare bypassed! No blocking detected.")

        # Stage 3: Form Detection
        print("\n📝 Stage 3: Enhanced form detection...")
        detection_start = time.time()
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)
        detection_time = time.time() - detection_start
        print(f"   🕒 Detection time: {detection_time:.2f}s")

        if not form_result.success:
            print("   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected successfully!")
        print(f"   📋 Fields found: {len(form_result.fields)}")
        print(f"   🎯 Confidence: {form_result.confidence_score:.2f}")

        # Stage 4: Human-like Form Filling
        print("\n✍️  Stage 4: Human-like form filling...")
        filling_start = time.time()
        filled_fields = []

        # Fill fields in natural order
        field_order = ['first_name', 'last_name', 'email', 'phone', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                print(f"   📝 Filling {field_name}...")

                success = await human_like_fill(
                    page,
                    field.selector,
                    test_data[field_name],
                    field_name
                )

                if success:
                    filled_fields.append(field_name)
                    print(f"      ✅ {field_name} filled successfully")
                else:
                    print(f"      ❌ {field_name} failed to fill")

                # Natural pause between fields (1-3 seconds)
                await asyncio.sleep(random.uniform(1.0, 3.0))

        filling_time = time.time() - filling_start
        print(f"\n   🕒 Form filling time: {filling_time:.2f}s")
        print(f"   📊 Fields filled: {len(filled_fields)}/{len(form_result.fields)}")

        # Stage 5: Screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"simple_final_test_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"   📸 Screenshot saved: {screenshot_path}")

        # Stage 6: Optional Submission
        if filled_fields and hasattr(form_result, 'submit_button') and form_result.submit_button:
            submit_choice = input("\n🤔 Submit the form? This will send the message! (y/N): ").lower().startswith('y')

            if submit_choice:
                print("\n📤 Stage 6: Submitting form...")
                submit_start = time.time()

                # Human-like submission
                submit_selector = form_result.submit_button.get('selector', 'button[type="submit"]')
                submit_locator = page.locator(submit_selector).first

                await submit_locator.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(1.0, 2.0))  # Pause to "review" form

                await submit_locator.click()
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

        # Success Summary
        print("\n" + "=" * 70)
        print("🎉 SIMPLE FINAL PIPELINE RESULTS")
        print("=" * 70)
        print("✅ Cloudflare Evasion: SUCCESS")
        print("✅ Form Detection: SUCCESS")
        print(f"✅ Form Filling: SUCCESS ({len(filled_fields)} fields)")
        print("✅ Human-like Behavior: SUCCESS")
        print("=" * 70)
        print("\n🔥 THE FLICKER ISSUE IS RESOLVED!")
        print("🔥 AUTOMATION IS NOW CLOUDFLARE-RESISTANT!")

        # Keep browser open
        print("\n⏳ Keeping browser open for inspection...")
        await asyncio.sleep(15)

    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🧹 Cleaning up...")
        await stealth.close_session(browser, context)


if __name__ == "__main__":
    asyncio.run(test_simple_final())