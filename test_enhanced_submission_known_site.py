#!/usr/bin/env python3
"""
Test enhanced submission behaviors specifically on Capital City CDJR site
to isolate and test the submission-phase improvements.
"""

import asyncio
import random
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


async def enhanced_human_form_fill(page, field_selector: str, value: str, field_name: str) -> bool:
    """Enhanced form filling with validation interactions."""
    try:
        locator = page.locator(field_selector).first
        await locator.wait_for(timeout=5000)

        print(f"      🎯 Locating {field_name} field...")

        # Scroll to field and pause (like human scanning)
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.4, 0.9))

        # Focus field (triggers validation)
        print(f"      👆 Focusing {field_name} field...")
        await locator.focus()
        await asyncio.sleep(random.uniform(0.2, 0.5))

        # Clear field
        await locator.fill("")
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Type with realistic human patterns
        print(f"      ⌨️  Typing {field_name} with human patterns...")
        for i, char in enumerate(str(value)):
            await locator.type(char)

            # Variable typing speed (faster in middle, slower at start/end)
            if i < 2 or i > len(value) - 3:
                delay = random.uniform(0.08, 0.18)  # Slower at edges
            else:
                delay = random.uniform(0.04, 0.12)  # Faster in middle

            await asyncio.sleep(delay)

        # Trigger blur event (validation)
        print(f"      🔍 Triggering validation for {field_name}...")
        await page.evaluate(f"document.querySelector('{field_selector}').blur()")
        await asyncio.sleep(random.uniform(0.3, 0.7))

        # Brief validation check pause
        await asyncio.sleep(random.uniform(0.2, 0.5))

        return True

    except Exception as e:
        print(f"      ❌ Failed to fill {field_name}: {e}")
        return False


async def enhanced_human_submission(page, submit_selector: str) -> bool:
    """Enhanced submission with extensive human-like behaviors."""
    try:
        print(f"\n📋 Enhanced Pre-Submission Review Phase:")

        # 1. Scroll up to review form (common human behavior)
        print("   📜 Scrolling up to review filled form...")
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await asyncio.sleep(random.uniform(1.5, 2.5))

        # 2. Scroll back down while "reading"
        print("   👀 Scrolling down while reviewing entries...")
        await page.evaluate("window.scrollBy({top: 200, behavior: 'smooth'})")
        await asyncio.sleep(random.uniform(1.0, 1.8))

        # 3. Random mouse movements (human nervousness)
        print("   🖱️  Natural mouse movements during review...")
        viewport = page.viewport_size
        for _ in range(random.randint(2, 4)):
            x = random.randint(200, viewport['width'] - 200)
            y = random.randint(200, viewport['height'] - 200)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.3, 0.8))

        # 4. Locate submit button and scroll to it
        submit_locator = page.locator(submit_selector).first
        print("   🎯 Locating submit button...")
        await submit_locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.8, 1.5))

        # 5. Hover over submit button (common before clicking)
        print("   🖱️  Hovering over submit button...")
        await submit_locator.hover()
        await asyncio.sleep(random.uniform(0.5, 1.2))

        # 6. Final hesitation (human behavior before committing)
        print("   ⏸️  Final review pause (human hesitation)...")
        await asyncio.sleep(random.uniform(3.0, 5.0))  # Longer hesitation

        # 7. Click submit button
        print("   📤 Clicking submit button...")
        await submit_locator.click()

        # 8. Post-click wait for processing
        print("   ⏳ Waiting for form processing...")
        await asyncio.sleep(random.uniform(3.0, 5.0))  # Longer wait

        return True

    except Exception as e:
        print(f"   ❌ Enhanced submission failed: {e}")
        return False


async def test_enhanced_submission_known_site():
    """Test enhanced submission on known working site."""
    print("🎯 ENHANCED SUBMISSION TEST - KNOWN WORKING SITE")
    print("🔥 Focus: Testing Submission-Phase Anti-Detection")
    print("=" * 75)

    # Known working site
    site_info = {
        'name': 'Capital City CDJR (Enhanced Submission Test)',
        'url': 'https://www.capcitycdjr.com/contact-us/',
        'location': 'Jefferson City, MO'
    }

    test_data = {
        'first_name': 'Miguel',
        'last_name': 'Montoya',
        'email': 'migueljmontoya@protonmail.com',
        'phone': '6503320719',
        'zip': '90066',
        'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel'
    }

    print(f"🏢 Testing Site: {site_info['name']}")
    print(f"🔗 URL: {site_info['url']}")
    print(f"📍 Location: {site_info['location']}")
    print("=" * 75)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        print(f"\n🚀 Phase 1: Cloudflare Stealth Browser Setup")
        browser, context, page = await stealth.create_stealth_session()
        print("   ✅ Enhanced stealth browser ready")

        print(f"\n🌐 Phase 2: Cloudflare Evasion Navigation")
        print("   ⚠️  BROWSER WILL OPEN - Watch the enhanced automation")
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, site_info['url'])

        if not nav_success:
            print("   ❌ Navigation failed - Cloudflare blocked")
            return

        print("   ✅ Navigation successful - Cloudflare bypassed")

        print(f"\n📝 Phase 3: Form Detection")
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)

        if not form_result.success:
            print("   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected - {len(form_result.fields)} fields found")
        print(f"   📋 Available fields: {list(form_result.fields.keys())}")

        print(f"\n✍️  Phase 4: Enhanced Human-like Form Filling")
        print("   🤖 Using enhanced validation-aware filling...")

        filled_count = 0
        field_order = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                print(f"\n   📝 Filling {field_name.replace('_', ' ').title()}:")

                success = await enhanced_human_form_fill(
                    page, field.selector, test_data[field_name], field_name
                )

                if success:
                    filled_count += 1
                    print(f"      ✅ {field_name.replace('_', ' ').title()} completed")
                else:
                    print(f"      ❌ {field_name.replace('_', ' ').title()} failed")

                # Natural pause between fields
                await asyncio.sleep(random.uniform(1.0, 2.5))

        print(f"\n   📊 Enhanced filling complete: {filled_count}/{len(form_result.fields)} fields")

        if filled_count == 0:
            print("   ❌ No fields filled - aborting test")
            return

        # Take pre-submission screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_submit_screenshot = f"enhanced_known_site_pre_{timestamp}.png"
        await page.screenshot(path=pre_submit_screenshot, full_page=True)
        print(f"   📸 Pre-submission screenshot: {pre_submit_screenshot}")

        print(f"\n📤 Phase 5: ENHANCED SUBMISSION WITH MAXIMUM ANTI-DETECTION")

        # Find submit button
        submit_selector = 'button[type="submit"]'  # Known to work on this site
        submit_count = await page.locator(submit_selector).count()

        if submit_count == 0:
            print("   ❌ No submit button found")
            return

        print(f"   🎯 Submit button found: {submit_selector}")

        # Enhanced submission with maximum anti-detection behaviors
        print("   🛡️  Applying maximum anti-detection measures...")
        submission_success = await enhanced_human_submission(page, submit_selector)

        if submission_success:
            print("   ✅ Form submitted with enhanced human behaviors")
        else:
            print("   ❌ Enhanced submission failed")

        print(f"\n📊 Phase 6: CRITICAL ANALYSIS - Checking for Blocking")

        # Extended wait for server response
        print("   ⏳ Extended wait for server response...")
        await asyncio.sleep(7)

        # Take post-submission screenshot
        post_submit_screenshot = f"enhanced_known_site_post_{timestamp}.png"
        await page.screenshot(path=post_submit_screenshot, full_page=True)
        print(f"   📸 Post-submission screenshot: {post_submit_screenshot}")

        # Check current page content
        try:
            current_url = page.url
            page_title = await page.title()
            body_text = await page.inner_text('body')

            print(f"   🔗 Current URL: {current_url}")
            print(f"   📄 Page Title: {page_title}")

            # Check for blocking indicators
            blocked_indicators = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'blocked because your browser',
                'access denied',
                'why have i been blocked',
                'security block',
                'blocked by cloudflare'
            ]

            blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)

            if blocked:
                print("   🚨 BLOCKING DETECTED - Cloudflare caught the submission!")
                print(f"   🔍 Blocking content preview: {body_text[:300]}...")

                # Find which indicator triggered
                for indicator in blocked_indicators:
                    if indicator in body_text.lower():
                        print(f"      🎯 Trigger: '{indicator}' found in page")
                        break
            else:
                print("   ✅ NO BLOCKING DETECTED - Submission bypassed security!")

            # Look for success indicators
            success_patterns = [
                'thank you',
                'we will be in touch',
                'submission received',
                'successfully sent',
                'we have received',
                'your message has been sent',
                'message sent',
                'form submitted'
            ]

            success_detected = any(pattern in body_text.lower() for pattern in success_patterns)

            if success_detected:
                print("   🎉 SUCCESS CONFIRMATION DETECTED!")
                for pattern in success_patterns:
                    if pattern in body_text.lower():
                        print(f"      ✅ Found success indicator: '{pattern}'")
            else:
                print("   ⚠️  No clear success confirmation found")

            print(f"\n🏆 FINAL ENHANCED SUBMISSION RESULT:")
            if not blocked and success_detected:
                print("   🎉 COMPLETE SUCCESS - Enhanced behaviors prevented detection!")
                print("   🛡️  All anti-detection measures worked perfectly")
            elif not blocked:
                print("   ✅ PARTIAL SUCCESS - No blocking, but unclear confirmation")
                print("   📋 Form likely submitted but server response unclear")
            else:
                print("   ❌ SUBMISSION STILL BLOCKED - Need further enhancements")
                print("   🔍 Cloudflare detected automation despite enhancements")

        except Exception as e:
            print(f"   ⚠️  Error analyzing page: {e}")

        # CRITICAL: Keep browser open for manual visual confirmation
        print(f"\n👁️  KEEPING BROWSER OPEN FOR 10 SECONDS FOR VISUAL CONFIRMATION")
        print("   👀 Check the browser window for:")
        print("   ✅ Success messages or thank you pages")
        print("   ❌ Error messages or blocking pages")
        print("   🔄 Redirect to confirmation pages")

        for i in range(10, 0, -1):
            print(f"   ⏱️  {i} seconds remaining for visual inspection...")
            await asyncio.sleep(1)

        print(f"\n📋 Screenshots saved:")
        print(f"   📸 Before: {pre_submit_screenshot}")
        print(f"   📸 After: {post_submit_screenshot}")

    except Exception as e:
        print(f"\n💥 Enhanced test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"\n🧹 Cleaning up...")
        await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 STARTING ENHANCED SUBMISSION TEST ON KNOWN WORKING SITE...")
    print("📋 Testing if enhanced behaviors prevent submission-phase blocking")
    print("👀 Browser will stay open for 10 seconds after submission")
    print("🎯 Focus: Analyzing what happens during form submission phase")
    print("⏸️  Press Ctrl+C to stop\n")

    try:
        await test_enhanced_submission_known_site()
        print("\n🏁 Enhanced submission analysis complete!")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())