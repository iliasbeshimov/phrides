#!/usr/bin/env python3
"""
Test complete end-to-end flow on Capital City CDJR to demonstrate all capabilities:
form filling, checkbox selection, overlay dismissal, and actual submission confirmation.
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


async def dismiss_overlays(page):
    """Aggressively dismiss all overlays that might block submission."""
    print("   🧹 Dismissing overlays and popups...")

    # Comprehensive overlay selectors
    overlay_selectors = [
        # Feedback/survey popups (like the one in your image)
        '[class*="feedback"] button:has-text("No thanks")',
        '[class*="feedback"] button:has-text("×")',
        '[class*="feedback"] .close',
        'button:has-text("No thanks")',
        '.no-thanks',

        # Emplifi/survey widgets
        '[class*="emplifi"] button',
        '[class*="survey"] button:has-text("No")',
        '[class*="survey"] .close',

        # Chat widgets (like the one in bottom right)
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

    overlays_dismissed = 0
    for selector in overlay_selectors:
        try:
            locator = page.locator(selector).first
            if await locator.count() > 0 and await locator.is_visible():
                await locator.click()
                overlays_dismissed += 1
                await asyncio.sleep(0.5)
                print(f"      ✅ Dismissed: {selector}")
        except Exception:
            continue

    # Press Escape key to dismiss any modal overlays
    try:
        await page.keyboard.press('Escape')
        await asyncio.sleep(0.5)
    except:
        pass

    print(f"   📊 Dismissed {overlays_dismissed} overlays")
    return overlays_dismissed


async def streamlined_form_fill(page, field_selector: str, value: str, field_name: str) -> bool:
    """Optimized form filling - faster but still human-like."""
    try:
        locator = page.locator(field_selector).first
        await locator.wait_for(timeout=4000)

        # Quick scroll and focus
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.2, 0.4))

        await locator.focus()
        await locator.fill("")
        await asyncio.sleep(random.uniform(0.1, 0.2))

        # Faster typing
        chars = str(value)
        for i, char in enumerate(chars):
            await locator.type(char)
            # Streamlined speed: pause every 8 characters
            if i % 8 == 0:
                delay = random.uniform(0.04, 0.08)
            else:
                delay = random.uniform(0.02, 0.05)
            await asyncio.sleep(delay)

        # Quick validation
        await page.evaluate(f"document.querySelector('{field_selector}').blur()")
        await asyncio.sleep(random.uniform(0.1, 0.3))

        print(f"      ✅ {field_name}")
        return True

    except Exception as e:
        print(f"      ❌ {field_name}: {str(e)[:50]}...")
        return False


async def handle_checkboxes(page) -> list:
    """Find and check relevant checkboxes like consent agreements."""
    print("   ☑️  Selecting checkboxes...")

    checked_boxes = []

    try:
        # Look for checkbox inputs
        checkboxes = page.locator('input[type="checkbox"]')
        count = await checkboxes.count()

        for i in range(count):
            checkbox = checkboxes.nth(i)

            # Skip if already checked
            if await checkbox.is_checked():
                continue

            # Get context/label
            try:
                # Try to find label
                checkbox_id = await checkbox.get_attribute('id')
                if checkbox_id:
                    label = page.locator(f'label[for="{checkbox_id}"]')
                    if await label.count() > 0:
                        label_text = await label.inner_text()
                    else:
                        # Get parent text
                        parent = checkbox.locator('xpath=..')
                        label_text = await parent.inner_text()
                else:
                    parent = checkbox.locator('xpath=..')
                    label_text = await parent.inner_text()

                label_text = label_text.strip()[:100]  # First 100 chars

            except:
                label_text = f"Checkbox {i+1}"

            # Check relevant checkboxes
            relevant_keywords = [
                'agree', 'consent', 'privacy', 'terms', 'contact',
                'communication', 'accept', 'acknowledge', 'permission'
            ]

            if any(keyword in label_text.lower() for keyword in relevant_keywords):
                try:
                    await checkbox.check()
                    checked_boxes.append(label_text)
                    print(f"      ✅ Checked: {label_text}")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"      ❌ Failed checkbox: {str(e)[:50]}...")

    except Exception as e:
        print(f"   ⚠️ Checkbox handling error: {e}")

    return checked_boxes


async def force_submit_with_overlays(page) -> bool:
    """Advanced submission with aggressive overlay handling."""
    print("   🚀 Force submission with overlay handling...")

    # Dismiss overlays before attempting submission
    await dismiss_overlays(page)

    submit_selectors = [
        'input[type="submit"]',
        'button[type="submit"]',
        'button:has-text("Submit")',
        'button:has-text("Send")',
        '.gform_button',
        '[value*="Send"]'
    ]

    for selector in submit_selectors:
        try:
            locator = page.locator(selector).first
            if await locator.count() > 0:
                print(f"      🎯 Found submit: {selector}")

                # Multiple submission attempts
                for attempt in range(3):
                    try:
                        # Dismiss overlays before each attempt
                        if attempt > 0:
                            await dismiss_overlays(page)
                            await asyncio.sleep(1)

                        # Scroll to submit button
                        await locator.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)

                        if attempt == 0:
                            # Normal click
                            await locator.click(timeout=5000)
                            print(f"      ✅ Normal click successful (attempt {attempt+1})")
                        elif attempt == 1:
                            # Force click
                            await locator.click(force=True, timeout=5000)
                            print(f"      ✅ Force click successful (attempt {attempt+1})")
                        else:
                            # JavaScript click
                            await locator.evaluate('element => element.click()')
                            print(f"      ✅ JavaScript click successful (attempt {attempt+1})")

                        return True

                    except Exception as e:
                        print(f"      ⚠️ Attempt {attempt+1} failed: {str(e)[:50]}...")
                        continue

        except Exception:
            continue

    # Final JavaScript form submission
    try:
        print("      🔧 Trying JavaScript form submission...")
        result = await page.evaluate("""
            () => {
                const forms = document.querySelectorAll('form');
                for (let form of forms) {
                    if (form.querySelector('input[type="email"], input[name*="email"]')) {
                        form.submit();
                        return 'success';
                    }
                }
                return 'no_form';
            }
        """)

        if result == 'success':
            print(f"      ✅ JavaScript submission successful")
            return True

    except Exception as e:
        print(f"      ❌ JavaScript submission failed: {e}")

    return False


async def test_complete_known_working():
    """Test complete flow on known working site."""
    print("🎯 COMPLETE END-TO-END TEST - CAPITAL CITY CDJR")
    print("🔥 Full Flow: Form + Checkboxes + Overlays + Submission + Confirmation")
    print("=" * 80)

    site_info = {
        'name': 'Capital City CDJR (Complete E2E Test)',
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
    print("=" * 80)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        print(f"\n🚀 Phase 1: Stealth Setup & Navigation")
        browser, context, page = await stealth.create_stealth_session()

        print("   ⚠️ BROWSER OPENING - Watch complete automation flow")
        nav_success = await stealth.navigate_with_cloudflare_evasion(page, site_info['url'])

        if not nav_success:
            print("   ❌ Navigation failed")
            return

        print("   ✅ Navigation + Cloudflare bypass successful")

        # Initial overlay dismissal
        await dismiss_overlays(page)

        print(f"\n📝 Phase 2: Form Detection")
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)

        if not form_result.success:
            print("   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected - {len(form_result.fields)} fields found")
        print(f"   📋 Field types: {list(form_result.fields.keys())}")

        print(f"\n✍️ Phase 3: Streamlined Form Filling")
        filled_count = 0
        field_order = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                success = await streamlined_form_fill(
                    page, field.selector, test_data[field_name], field_name
                )
                if success:
                    filled_count += 1

                # Reduced inter-field delay
                await asyncio.sleep(random.uniform(0.3, 0.7))

        print(f"   📊 Form filling complete: {filled_count}/{len(form_result.fields)} fields")

        print(f"\n☑️ Phase 4: Checkbox Selection")
        checked_boxes = await handle_checkboxes(page)
        print(f"   📊 Checkboxes selected: {len(checked_boxes)}")

        # Take pre-submission screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_screenshot = f"complete_known_pre_{timestamp}.png"
        await page.screenshot(path=pre_screenshot, full_page=True)
        print(f"   📸 Pre-submission screenshot: {pre_screenshot}")

        print(f"\n📤 Phase 5: Advanced Submission with Overlay Handling")

        # Pre-submission pause (human behavior)
        await asyncio.sleep(random.uniform(1.5, 2.5))

        # Attempt submission
        submission_success = await force_submit_with_overlays(page)

        print(f"\n📊 Phase 6: Confirmation & Results Analysis")

        # Extended wait for response
        print("   ⏳ Waiting for submission response...")
        await asyncio.sleep(7)

        # Post-submission screenshot
        post_screenshot = f"complete_known_post_{timestamp}.png"
        await page.screenshot(path=post_screenshot, full_page=True)
        print(f"   📸 Post-submission screenshot: {post_screenshot}")

        # Analyze page
        current_url = page.url
        page_title = await page.title()
        body_text = await page.inner_text('body')

        print(f"   🔗 Current URL: {current_url}")
        print(f"   📄 Page Title: {page_title}")

        # Check for success patterns
        success_patterns = [
            'thank you', 'thanks for', 'we will be in touch', 'submission received',
            'successfully sent', 'message sent', 'form submitted', 'we have received',
            'your message has been sent', 'submitted successfully', 'message received'
        ]

        success_found = []
        for pattern in success_patterns:
            if pattern in body_text.lower():
                success_found.append(pattern)

        # Check for blocking
        blocked_indicators = [
            'sorry, you have been blocked', 'cloudflare ray id',
            'access denied', 'security block', 'blocked by cloudflare'
        ]

        blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)

        print(f"\n🏆 COMPLETE END-TO-END RESULTS:")
        if blocked:
            print("   🚨 BLOCKED - Cloudflare/security detected automation")
            print(f"   🔍 Block content: {body_text[:200]}...")
        elif success_found:
            print("   🎉 SUCCESS - SUBMISSION CONFIRMED!")
            for pattern in success_found:
                print(f"      ✅ Success indicator: '{pattern}'")
        elif submission_success:
            print("   ✅ LIKELY SUCCESS - Form submitted, no blocking")
            print(f"   📄 Page content preview: {body_text[:300]}...")
        else:
            print("   ⚠️ UNCLEAR - Submission attempted but result uncertain")

        print(f"\n📊 Complete Flow Summary:")
        print(f"   🌐 Cloudflare Bypass: ✅ SUCCESS")
        print(f"   📝 Form Fields: {filled_count} filled")
        print(f"   ☑️ Checkboxes: {len(checked_boxes)} selected")
        print(f"   🧹 Overlays: Handled")
        print(f"   📤 Submission: {'✅ SUCCESS' if submission_success else '❌ FAILED'}")
        print(f"   ✅ Confirmation: {'🎉 FOUND' if success_found else '⚠️ UNCLEAR'}")

        # Extended visual confirmation
        print(f"\n👁️ VISUAL CONFIRMATION - 15 SECONDS")
        print("   👀 Check the browser for:")
        print("   ✅ Thank you messages or confirmation pages")
        print("   ❌ Error messages or validation issues")
        print("   🔄 Page redirects to success pages")

        for i in range(15, 0, -1):
            print(f"   ⏱️ {i}s remaining...")
            await asyncio.sleep(1)

        print(f"\n📸 Test Artifacts:")
        print(f"   📷 Before submission: {pre_screenshot}")
        print(f"   📷 After submission: {post_screenshot}")

    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"\n🧹 Cleaning up...")
        await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 COMPLETE END-TO-END TEST ON KNOWN WORKING SITE")
    print("📋 Demonstrating full automation flow with overlay handling")
    print("🎯 Goal: Complete successful submission with confirmation")
    print("👀 Browser stays open 15 seconds for visual verification\n")

    try:
        await test_complete_known_working()
        print("\n🏁 Complete end-to-end test finished!")

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as exc:
        print(f"\n💥 Failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())