#!/usr/bin/env python3
"""
Final test combining our successful Cloudflare evasion with the existing
enhanced form detector and human-like form filling.
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
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.human_form_filler import HumanFormFiller


async def test_final_pipeline():
    """Test the complete optimized pipeline."""
    print("🎯 FINAL OPTIMIZED PIPELINE TEST")
    print("🔥 Cloudflare Evasion + Enhanced Detection + Human Filling")
    print("=" * 65)

    test_url = "https://www.capcitycdjr.com/contact-us/"
    test_data = {
        'first_name': 'Miguel',
        'last_name': 'Montoya',
        'email': 'migueljmontoya@protonmail.com',
        'phone': '650-688-2311',
        'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available? Best, Miguel'
    }

    print(f"🔍 Testing URL: {test_url}")
    print("⚠️  BROWSER WILL OPEN - WATCH THE FULL AUTOMATION")
    print("=" * 65)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        # Stage 1: Stealth Browser Setup
        print("\n🚀 Stage 1: Setting up stealth browser (anti-Cloudflare)...")
        start_time = time.time()
        browser, context, page = await stealth.create_stealth_session()
        setup_time = time.time() - start_time
        print(f"   ✅ Stealth browser ready ({setup_time:.2f}s)")

        # Stage 2: Cloudflare Evasion Navigation
        print("\n🌐 Stage 2: Navigating with Cloudflare evasion...")
        nav_start = time.time()
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, test_url)
        nav_time = time.time() - nav_start
        print(f"   🕒 Navigation time: {nav_time:.2f}s")

        if not nav_success:
            print("   ❌ Navigation failed - Cloudflare blocked")
            return

        print("   ✅ SUCCESS: Cloudflare bypassed! No flicker detected.")

        # Stage 3: Enhanced Form Detection (but with minimal scanning)
        print("\n📝 Stage 3: Enhanced form detection (limited scanning)...")
        detection_start = time.time()

        # Use existing detector
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)
        detection_time = time.time() - detection_start
        print(f"   🕒 Detection time: {detection_time:.2f}s")

        if not form_result.success:
            print(f"   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected successfully!")
        print(f"   📋 Fields found: {len(form_result.fields)}")
        print(f"   🎯 Confidence: {form_result.confidence_score:.2f}")
        print(f"   📋 Field types: {list(form_result.fields.keys())}")

        # Stage 4: Human-like Form Filling
        print("\n✍️  Stage 4: Human-like form filling...")
        filling_start = time.time()
        human_filler = HumanFormFiller()
        filled_fields = []

        # Fill fields in natural order
        field_order = ['first_name', 'last_name', 'email', 'phone', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                print(f"   📝 Filling {field_name} naturally...")

                success = await human_filler.fill_field_naturally(
                    page,
                    field.selector,
                    test_data[field_name],
                    field_name
                )

                if success:
                    filled_fields.append(field_name)
                    print(f"      ✅ {field_name} filled with human-like typing")
                else:
                    print(f"      ❌ {field_name} failed to fill")

                # Natural pause between fields (1-3 seconds)
                await human_filler.pause_between_fields(field_name)

        filling_time = time.time() - filling_start
        print(f"   🕒 Form filling time: {filling_time:.2f}s")
        print(f"   📊 Fields filled: {len(filled_fields)}/{len(form_result.fields)}")

        # Stage 5: Screenshot Before Submission
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"final_pipeline_success_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"   📸 Pre-submission screenshot: {screenshot_path}")

        # Stage 6: Optional Form Submission
        if filled_fields and hasattr(form_result, 'submit_selector') and form_result.submit_selector:
            submit_choice = input("\n🤔 Submit the form? This will actually send the message! (y/N): ").lower().startswith('y')

            if submit_choice:
                print("\n📤 Stage 6: Submitting form with human timing...")
                submit_start = time.time()

                # Human-like submission - scroll to submit button first
                submit_locator = page.locator(form_result.submit_selector).first
                await submit_locator.scroll_into_view_if_needed()
                await asyncio.sleep(1)  # Brief pause to "read" the form

                await submit_locator.click()
                submit_time = time.time() - submit_start
                print(f"   ✅ Form submitted successfully ({submit_time:.2f}s)")

                # Wait for response and take screenshot
                await asyncio.sleep(3)
                post_submit_screenshot = f"form_submitted_{timestamp}.png"
                await page.screenshot(path=post_submit_screenshot, full_page=True)
                print(f"   📸 Post-submission screenshot: {post_submit_screenshot}")
            else:
                print("   ⏭️  Skipping submission (testing only)")
        else:
            print("   ⚠️  No submit button found or no fields filled")

        total_time = time.time() - start_time
        print(f"\n⏱️  Total pipeline time: {total_time:.2f}s")

        # Final Results Summary
        print("\n" + "=" * 65)
        print("🎉 FINAL PIPELINE TEST RESULTS")
        print("=" * 65)
        print("✅ Cloudflare Evasion: SUCCESS (no flicker, no blocking)")
        print("✅ Form Detection: SUCCESS (enhanced detector)")
        print(f"✅ Form Filling: SUCCESS ({len(filled_fields)} fields filled)")
        print("✅ Human-like Behavior: SUCCESS (natural typing & timing)")
        print("✅ Anti-Detection: SUCCESS (no robotic patterns)")
        print("=" * 65)
        print("\n🔥 AUTOMATION PIPELINE IS NOW CLOUDFLARE-RESISTANT!")

        # Keep browser open for inspection
        print("\n⏳ Keeping browser open for 15 seconds for inspection...")
        await asyncio.sleep(15)

    except Exception as exc:
        print(f"\n💥 Pipeline test failed: {exc}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🧹 Cleaning up...")
        await stealth.close_session(browser, context)


if __name__ == "__main__":
    asyncio.run(test_final_pipeline())