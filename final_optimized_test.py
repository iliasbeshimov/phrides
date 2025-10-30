#!/usr/bin/env python3
"""
Final optimized test combining successful enhanced form filling with simpler submission.
Based on previous test showing that enhanced behaviors prevent Cloudflare blocking.
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


async def optimized_human_form_fill(page, field_selector: str, value: str, field_name: str) -> bool:
    """Optimized form filling with validation but without excessive delays."""
    try:
        locator = page.locator(field_selector).first
        await locator.wait_for(timeout=5000)

        print(f"      🎯 Filling {field_name}...")

        # Natural field interaction
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.3, 0.6))

        # Focus field (important for validation)
        await locator.focus()
        await asyncio.sleep(random.uniform(0.2, 0.4))

        # Clear and type with human patterns
        await locator.fill("")
        await asyncio.sleep(random.uniform(0.1, 0.2))

        # Human-like typing
        for i, char in enumerate(str(value)):
            await locator.type(char)
            # Variable speed: slower at start/end, faster in middle
            if i < 2 or i > len(value) - 3:
                delay = random.uniform(0.06, 0.14)
            else:
                delay = random.uniform(0.03, 0.08)
            await asyncio.sleep(delay)

        # Trigger validation event
        await page.evaluate(f"document.querySelector('{field_selector}').blur()")
        await asyncio.sleep(random.uniform(0.2, 0.4))

        return True

    except Exception as e:
        print(f"      ❌ Failed to fill {field_name}: {e}")
        return False


async def optimized_human_submission(page) -> bool:
    """Optimized submission with essential human behaviors but reliable execution."""
    try:
        print(f"\n📤 Optimized Human Submission:")

        # Brief form review (essential human behavior)
        print("   👀 Brief form review...")
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Scroll back to form
        await page.evaluate("window.scrollBy({top: 300, behavior: 'smooth'})")
        await asyncio.sleep(random.uniform(0.8, 1.5))

        # Find submit button with multiple selectors
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            '.gform_button'
        ]

        submit_locator = None
        for selector in submit_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0 and await locator.is_visible():
                    submit_locator = locator
                    print(f"   🎯 Found submit button: {selector}")
                    break
            except:
                continue

        if not submit_locator:
            print("   ❌ No visible submit button found")
            return False

        # Human hesitation before clicking
        print("   ⏸️  Pre-submission pause...")
        await asyncio.sleep(random.uniform(1.5, 3.0))

        # Click submit
        print("   📤 Clicking submit...")
        await submit_locator.click()

        # Wait for processing
        print("   ⏳ Waiting for form processing...")
        await asyncio.sleep(random.uniform(3.0, 5.0))

        return True

    except Exception as e:
        print(f"   ❌ Optimized submission failed: {e}")
        return False


async def final_optimized_test():
    """Final optimized test for successful form submission."""
    print("🎯 FINAL OPTIMIZED SUBMISSION TEST")
    print("🔥 Combining Enhanced Behaviors + Reliable Execution")
    print("=" * 70)

    site_info = {
        'name': 'Capital City CDJR (Final Optimized Test)',
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

    print(f"🏢 Site: {site_info['name']}")
    print(f"🔗 URL: {site_info['url']}")
    print(f"👤 Contact: {test_data['first_name']} {test_data['last_name']}")
    print("=" * 70)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        print(f"\n🚀 Phase 1: Stealth Browser")
        browser, context, page = await stealth.create_stealth_session()
        print("   ✅ Cloudflare stealth ready")

        print(f"\n🌐 Phase 2: Navigation")
        print("   ⚠️  BROWSER OPENING - Watch the optimized automation")
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, site_info['url'])

        if not nav_success:
            print("   ❌ Navigation blocked")
            return

        print("   ✅ Navigation successful - Cloudflare bypassed")

        print(f"\n📝 Phase 3: Form Detection")
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)

        if not form_result.success:
            print("   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected - {len(form_result.fields)} fields")

        print(f"\n✍️  Phase 4: Optimized Form Filling")
        filled_count = 0
        field_order = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                success = await optimized_human_form_fill(
                    page, field.selector, test_data[field_name], field_name
                )

                if success:
                    filled_count += 1
                    print(f"      ✅ {field_name.replace('_', ' ').title()}")

                # Natural pause between fields
                await asyncio.sleep(random.uniform(0.5, 1.2))

        print(f"   📊 Filled: {filled_count}/{len(form_result.fields)} fields")

        # Pre-submission screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_screenshot = f"final_optimized_pre_{timestamp}.png"
        await page.screenshot(path=pre_screenshot, full_page=True)
        print(f"   📸 Pre-submission: {pre_screenshot}")

        print(f"\n📤 Phase 5: Optimized Submission")
        submission_success = await optimized_human_submission(page)

        # Post-submission analysis
        print(f"\n📊 Phase 6: Results Analysis")

        # Extended wait for response
        await asyncio.sleep(5)

        # Post-submission screenshot
        post_screenshot = f"final_optimized_post_{timestamp}.png"
        await page.screenshot(path=post_screenshot, full_page=True)
        print(f"   📸 Post-submission: {post_screenshot}")

        # Analyze page content
        try:
            current_url = page.url
            page_title = await page.title()
            body_text = await page.inner_text('body')

            print(f"   🔗 URL: {current_url}")
            print(f"   📄 Title: {page_title}")

            # Check for blocking
            blocked_indicators = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'blocked because your browser',
                'access denied',
                'security block'
            ]

            blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)

            # Check for success
            success_patterns = [
                'thank you',
                'we will be in touch',
                'submission received',
                'successfully sent',
                'message sent',
                'form submitted'
            ]

            success_detected = any(pattern in body_text.lower() for pattern in success_patterns)

            print(f"\n🏆 FINAL RESULT:")
            if blocked:
                print("   🚨 BLOCKED - Cloudflare detected automation")
                print(f"   🔍 Content: {body_text[:200]}...")
            elif success_detected:
                print("   🎉 SUCCESS - Form submitted successfully!")
                for pattern in success_patterns:
                    if pattern in body_text.lower():
                        print(f"      ✅ Confirmation: '{pattern}' found")
            elif submission_success:
                print("   ✅ LIKELY SUCCESS - Form submitted, no blocking detected")
            else:
                print("   ⚠️  UNCLEAR - Submission attempted but result unclear")

        except Exception as e:
            print(f"   ⚠️  Analysis error: {e}")

        # Visual confirmation period
        print(f"\n👁️  VISUAL CONFIRMATION - 10 SECONDS")
        print("   👀 Check browser for:")
        print("   ✅ Thank you messages")
        print("   ❌ Error or blocking pages")
        print("   🔄 Page redirects")

        for i in range(10, 0, -1):
            print(f"   ⏱️  {i}s...")
            await asyncio.sleep(1)

        print(f"\n📋 Artifacts:")
        print(f"   📸 Before: {pre_screenshot}")
        print(f"   📸 After: {post_screenshot}")

    except Exception as e:
        print(f"\n💥 Test failed: {e}")

    finally:
        print(f"\n🧹 Cleanup...")
        await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 FINAL OPTIMIZED SUBMISSION TEST")
    print("📋 Combines successful enhanced behaviors with reliable execution")
    print("🎯 Goal: Successful form submission without detection")
    print("👀 Browser stays open 10 seconds for confirmation\n")

    try:
        await final_optimized_test()
        print("\n🏁 Final optimized test complete!")

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as exc:
        print(f"\n💥 Failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())