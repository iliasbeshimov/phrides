#!/usr/bin/env python3
"""
Advanced anti-detection test with maximum submission-phase stealth.
Based on analysis showing that form filling works but submission gets blocked.
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


async def ultra_stealth_form_fill(page, field_selector: str, value: str, field_name: str) -> bool:
    """Ultra-stealth form filling with maximum human simulation."""
    try:
        locator = page.locator(field_selector).first
        await locator.wait_for(timeout=5000)

        # Human scanning behavior
        await locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(0.5, 1.2))

        # Multiple focus attempts (humans sometimes miss)
        for attempt in range(random.randint(1, 2)):
            await locator.focus()
            await asyncio.sleep(random.uniform(0.2, 0.5))

        # Clear with backspace simulation
        current_value = await locator.input_value()
        if current_value:
            for _ in range(len(current_value)):
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.03, 0.08))

        await asyncio.sleep(random.uniform(0.3, 0.8))

        # Ultra-natural typing with micro-pauses
        chars = str(value)
        for i, char in enumerate(chars):
            # Occasional hesitation (thinking)
            if random.random() < 0.08:  # 8% chance
                await asyncio.sleep(random.uniform(0.4, 0.9))

            await locator.type(char)

            # Variable speed based on character type
            if char.isspace():
                delay = random.uniform(0.08, 0.15)  # Pause on spaces
            elif char.isdigit():
                delay = random.uniform(0.05, 0.12)  # Steady on numbers
            elif i == 0:
                delay = random.uniform(0.12, 0.20)  # Slow start
            elif i == len(chars) - 1:
                delay = random.uniform(0.08, 0.15)  # Careful end
            else:
                delay = random.uniform(0.04, 0.10)  # Normal speed

            await asyncio.sleep(delay)

        # Natural field exit
        await asyncio.sleep(random.uniform(0.2, 0.6))
        await page.keyboard.press('Tab')  # Tab out naturally
        await asyncio.sleep(random.uniform(0.3, 0.8))

        print(f"      ✅ {field_name}")
        return True

    except Exception as e:
        print(f"      ❌ {field_name}: {str(e)[:50]}...")
        return False


async def ultra_stealth_checkbox_handling(page) -> list:
    """Ultra-stealth checkbox selection with human patterns."""
    print("   ☑️  Ultra-stealth checkbox selection...")

    checked_boxes = []

    try:
        checkboxes = page.locator('input[type="checkbox"]')
        count = await checkboxes.count()

        if count == 0:
            print("      ℹ️  No checkboxes found")
            return checked_boxes

        for i in range(count):
            checkbox = checkboxes.nth(i)

            if await checkbox.is_checked():
                continue

            # Get checkbox context
            try:
                checkbox_id = await checkbox.get_attribute('id')
                if checkbox_id:
                    label = page.locator(f'label[for="{checkbox_id}"]')
                    if await label.count() > 0:
                        label_text = await label.inner_text()
                    else:
                        parent = checkbox.locator('xpath=..')
                        label_text = await parent.inner_text()
                else:
                    parent = checkbox.locator('xpath=..')
                    label_text = await parent.inner_text()

                label_text = label_text.strip()[:100]
            except:
                label_text = f"Checkbox {i+1}"

            # Check relevant boxes with human behavior
            relevant = any(keyword in label_text.lower() for keyword in [
                'agree', 'consent', 'privacy', 'terms', 'contact',
                'communication', 'accept', 'acknowledge', 'permission'
            ])

            if relevant:
                # Human scanning of checkbox
                await checkbox.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.8, 1.5))

                # Hover before click (human behavior)
                await checkbox.hover()
                await asyncio.sleep(random.uniform(0.3, 0.8))

                # Click with slight delay
                await checkbox.check()
                checked_boxes.append(label_text)
                print(f"      ✅ Checked: {label_text}")

                # Post-check pause
                await asyncio.sleep(random.uniform(0.5, 1.2))

    except Exception as e:
        print(f"   ⚠️ Checkbox error: {e}")

    return checked_boxes


async def maximum_stealth_submission(page) -> bool:
    """Maximum stealth submission with extensive human simulation."""
    try:
        print(f"\n🛡️ MAXIMUM STEALTH SUBMISSION PROTOCOL")

        # Phase 1: Extended form review (critical human behavior)
        print("   📋 Phase 1: Extended Form Review")

        # Scroll to top and review entire form
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await asyncio.sleep(random.uniform(2.0, 3.5))

        # Slow scroll through form sections
        form_height = await page.evaluate("document.body.scrollHeight")
        scroll_steps = random.randint(3, 5)

        for step in range(scroll_steps):
            scroll_position = (form_height // scroll_steps) * (step + 1)
            await page.evaluate(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")
            await asyncio.sleep(random.uniform(1.5, 2.8))

            # Random mouse movements during review
            viewport = page.viewport_size
            x = random.randint(100, viewport['width'] - 100)
            y = random.randint(100, viewport['height'] - 100)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.3, 0.7))

        # Phase 2: Submit button location and hesitation
        print("   🎯 Phase 2: Submit Button Analysis")

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
                    print(f"      🎯 Located: {selector}")
                    break
            except:
                continue

        if not submit_locator:
            print("      ❌ No submit button found")
            return False

        # Scroll to submit area slowly
        await submit_locator.scroll_into_view_if_needed()
        await asyncio.sleep(random.uniform(1.2, 2.0))

        # Phase 3: Pre-submission mouse behavior
        print("   🖱️ Phase 3: Pre-submission Mouse Behavior")

        # Multiple hover attempts (indecision simulation)
        for _ in range(random.randint(2, 4)):
            await submit_locator.hover()
            await asyncio.sleep(random.uniform(0.8, 1.5))

            # Move mouse away (hesitation)
            box = await submit_locator.bounding_box()
            if box:
                away_x = box['x'] + random.randint(-100, 100)
                away_y = box['y'] + random.randint(-50, 50)
                await page.mouse.move(away_x, away_y)
                await asyncio.sleep(random.uniform(0.5, 1.2))

        # Final hover on submit
        await submit_locator.hover()
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Phase 4: Maximum hesitation (critical for human simulation)
        print("   ⏸️ Phase 4: Maximum Pre-Submission Hesitation")
        hesitation_time = random.uniform(4.0, 8.0)
        print(f"      ⏱️ Hesitating for {hesitation_time:.1f} seconds...")

        # Simulate reading terms/privacy during hesitation
        steps = int(hesitation_time * 2)  # Check every 0.5 seconds
        for i in range(steps):
            # Occasional mouse micro-movements
            if random.random() < 0.3:
                current_pos = await page.evaluate("({x: window.mouseX || 0, y: window.mouseY || 0})")
                new_x = random.randint(-10, 10)
                new_y = random.randint(-10, 10)
                await page.mouse.move(new_x, new_y, steps=random.randint(1, 3))

            await asyncio.sleep(0.5)

        # Phase 5: Final submission with multiple fallbacks
        print("   📤 Phase 5: Multi-Method Submission")

        # Method 1: Natural click with pre-click pause
        try:
            print("      🎯 Method 1: Natural click...")
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await submit_locator.click(timeout=8000)
            print("      ✅ Natural click successful")
            return True
        except Exception as e:
            print(f"      ⚠️ Natural click failed: {str(e)[:50]}...")

        # Method 2: Force click after delay
        try:
            print("      🔧 Method 2: Force click...")
            await asyncio.sleep(2)
            await submit_locator.click(force=True, timeout=8000)
            print("      ✅ Force click successful")
            return True
        except Exception as e:
            print(f"      ⚠️ Force click failed: {str(e)[:50]}...")

        # Method 3: JavaScript with stealth wrapper
        try:
            print("      💻 Method 3: Stealth JavaScript...")
            await asyncio.sleep(2)

            # Inject human-like click simulation
            await page.evaluate("""
                () => {
                    const button = document.querySelector('button[type="submit"], input[type="submit"]');
                    if (button) {
                        // Simulate human click events
                        const events = ['mousedown', 'mouseup', 'click'];
                        events.forEach(eventType => {
                            const event = new MouseEvent(eventType, {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            button.dispatchEvent(event);
                        });

                        // Backup form submission
                        const form = button.closest('form');
                        if (form) {
                            form.submit();
                        }
                        return true;
                    }
                    return false;
                }
            """)
            print("      ✅ Stealth JavaScript successful")
            return True
        except Exception as e:
            print(f"      ❌ Stealth JavaScript failed: {e}")

        return False

    except Exception as e:
        print(f"   ❌ Maximum stealth submission failed: {e}")
        return False


async def advanced_anti_detection_test():
    """Advanced anti-detection test with maximum stealth measures."""
    print("🔒 ADVANCED ANTI-DETECTION TEST")
    print("🛡️ Maximum Stealth: Extended Human Behaviors + Multiple Submission Methods")
    print("=" * 80)

    site_info = {
        'name': 'Capital City CDJR (Advanced Anti-Detection)',
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

    print(f"🏢 Target: {site_info['name']}")
    print(f"🔗 URL: {site_info['url']}")
    print(f"👤 Contact: {test_data['first_name']} {test_data['last_name']}")
    print("=" * 80)

    stealth = CloudflareStealth()
    browser = None
    context = None

    try:
        print(f"\n🚀 Phase 1: Maximum Stealth Browser")
        browser, context, page = await stealth.create_stealth_session()

        # Additional stealth measures
        await page.add_init_script("""
            // Override timing functions to appear more human
            const originalSetTimeout = window.setTimeout;
            window.setTimeout = function(callback, delay) {
                return originalSetTimeout(callback, delay + Math.random() * 50);
            };

            // Add human-like properties
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        print("   ✅ Ultra-stealth browser ready")

        print(f"\n🌐 Phase 2: Enhanced Navigation")
        print("   ⚠️ BROWSER OPENING - Watch maximum stealth automation")

        # Pre-navigation delay
        await asyncio.sleep(random.uniform(2.0, 4.0))

        nav_success = await stealth.navigate_with_cloudflare_evasion(page, site_info['url'])

        if not nav_success:
            print("   ❌ Navigation blocked")
            return

        print("   ✅ Navigation successful with enhanced evasion")

        # Extended page load simulation
        print("   ⏳ Extended page analysis...")
        await asyncio.sleep(random.uniform(3.0, 6.0))

        print(f"\n📝 Phase 3: Form Detection")
        detector = EnhancedFormDetector()
        form_result = await detector.detect_contact_form(page)

        if not form_result.success:
            print("   ❌ Form detection failed")
            return

        print(f"   ✅ Form detected - {len(form_result.fields)} fields")

        print(f"\n✍️ Phase 4: Ultra-Stealth Form Filling")
        filled_count = 0
        field_order = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']

        for field_name in field_order:
            if field_name in form_result.fields and field_name in test_data:
                field = form_result.fields[field_name]
                print(f"\n   📝 Ultra-filling {field_name.replace('_', ' ').title()}:")

                success = await ultra_stealth_form_fill(
                    page, field.selector, test_data[field_name], field_name
                )

                if success:
                    filled_count += 1

                # Extended inter-field delay
                await asyncio.sleep(random.uniform(1.5, 3.0))

        print(f"\n   📊 Ultra-stealth filling: {filled_count}/{len(form_result.fields)} fields")

        print(f"\n☑️ Phase 5: Ultra-Stealth Checkbox Handling")
        checked_boxes = await ultra_stealth_checkbox_handling(page)
        print(f"   📊 Checkboxes processed: {len(checked_boxes)}")

        # Pre-submission screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_screenshot = f"advanced_anti_detection_pre_{timestamp}.png"
        await page.screenshot(path=pre_screenshot, full_page=True)
        print(f"\n   📸 Pre-submission: {pre_screenshot}")

        print(f"\n🔒 Phase 6: MAXIMUM STEALTH SUBMISSION")
        submission_success = await maximum_stealth_submission(page)

        print(f"\n📊 Phase 7: Advanced Results Analysis")

        # Extended wait for server processing
        print("   ⏳ Extended wait for response...")
        await asyncio.sleep(10)

        # Post-submission screenshot
        post_screenshot = f"advanced_anti_detection_post_{timestamp}.png"
        await page.screenshot(path=post_screenshot, full_page=True)
        print(f"   📸 Post-submission: {post_screenshot}")

        # Comprehensive page analysis
        try:
            current_url = page.url
            page_title = await page.title()
            body_text = await page.inner_text('body')

            print(f"   🔗 URL: {current_url}")
            print(f"   📄 Title: {page_title}")

            # Advanced blocking detection
            blocking_patterns = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'access denied',
                'security block',
                'attention required',
                'blocked because',
                'why have i been blocked',
                'checking your browser',
                'please complete the security check'
            ]

            blocked = any(pattern in body_text.lower() for pattern in blocking_patterns)

            # Enhanced success detection
            success_patterns = [
                'thank you',
                'thanks for',
                'we will be in touch',
                'submission received',
                'successfully sent',
                'message sent',
                'form submitted',
                'we have received',
                'your message has been sent',
                'submitted successfully',
                'we\'ll be in touch',
                'contact request received'
            ]

            success_detected = any(pattern in body_text.lower() for pattern in success_patterns)

            print(f"\n🏆 ADVANCED ANTI-DETECTION RESULTS:")

            if blocked:
                print("   🚨 STILL BLOCKED - Maximum stealth insufficient")
                print(f"   🔍 Block indicators found:")
                for pattern in blocking_patterns:
                    if pattern in body_text.lower():
                        print(f"      ❌ '{pattern}'")
                print(f"   📄 Content preview: {body_text[:300]}...")

            elif success_detected:
                print("   🎉 SUCCESS - MAXIMUM STEALTH WORKED!")
                print(f"   ✅ Success indicators found:")
                for pattern in success_patterns:
                    if pattern in body_text.lower():
                        print(f"      ✅ '{pattern}'")

            elif submission_success:
                print("   ✅ LIKELY SUCCESS - No blocking detected")
                print(f"   📄 Response preview: {body_text[:300]}...")

            else:
                print("   ⚠️ UNCLEAR - Need manual verification")

        except Exception as e:
            print(f"   ⚠️ Analysis error: {e}")

        # Extended visual confirmation
        print(f"\n👁️ EXTENDED VISUAL CONFIRMATION - 15 SECONDS")
        print("   👀 Manual verification required:")
        print("   ✅ Look for success/thank you messages")
        print("   ❌ Check for blocking or error pages")
        print("   🔄 Verify any page redirects")
        print("   📧 Check if confirmation emails would be sent")

        for i in range(15, 0, -1):
            print(f"   ⏱️ {i}s remaining for manual verification...")
            await asyncio.sleep(1)

        print(f"\n📋 Test Artifacts:")
        print(f"   📸 Before: {pre_screenshot}")
        print(f"   📸 After: {post_screenshot}")

    except Exception as e:
        print(f"\n💥 Advanced test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"\n🧹 Cleanup...")
        await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 ADVANCED ANTI-DETECTION TEST")
    print("🛡️ Maximum stealth measures + Extended human behaviors")
    print("🎯 Goal: Bypass Cloudflare submission-phase detection")
    print("👀 Browser stays open 15 seconds for verification\n")

    try:
        await advanced_anti_detection_test()
        print("\n🏁 Advanced anti-detection test complete!")

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as exc:
        print(f"\n💥 Failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())