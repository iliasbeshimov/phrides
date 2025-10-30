#!/usr/bin/env python3
"""
Complete end-to-end test: Random dealership, form fill, checkboxes, dropdowns,
overlay dismissal, and actual submission confirmation.
Optimized for speed while maintaining anti-detection.
"""

import asyncio
import csv
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


class CompleteEndToEndTester:
    """Complete form submission with overlay handling and checkbox/dropdown support."""

    def __init__(self):
        self.test_data = {
            'first_name': 'Miguel',
            'last_name': 'Montoya',
            'email': 'migueljmontoya@protonmail.com',
            'phone': '6503320719',
            'zip_code': '90066',
            'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel'
        }

    def get_random_dealership(self) -> dict:
        """Get a random dealership with valid website."""
        try:
            with open('Dealerships.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                valid_dealers = []

                for row in reader:
                    website = row.get('website', '').strip()
                    dealer_name = row.get('dealer_name', '').strip()

                    if website and website not in ['', 'N/A', 'None'] and website.startswith('http'):
                        valid_dealers.append({
                            'name': dealer_name,
                            'website': website,
                            'city': row.get('city', ''),
                            'state': row.get('state', ''),
                            'phone': row.get('phone', '')
                        })

                if valid_dealers:
                    # Select random dealership
                    selected = random.choice(valid_dealers)
                    print(f"🎲 Randomly selected: {selected['name']}")
                    return selected

        except Exception as e:
            print(f"Error reading CSV: {e}")

        # Fallback to Capital City for testing
        return {
            'name': 'Capital City CDJR (Fallback)',
            'website': 'https://www.capcitycdjr.com/contact-us/',
            'city': 'Jefferson City',
            'state': 'MO',
            'phone': '573-635-6137'
        }

    async def dismiss_overlays(self, page):
        """Dismiss common overlays that block form submission."""
        print("   🧹 Dismissing overlays and popups...")

        # Common overlay selectors
        overlay_selectors = [
            # Feedback/survey popups
            '[class*="feedback"] button:has-text("No thanks")',
            '[class*="feedback"] button:has-text("×")',
            '[class*="feedback"] .close',
            'button:has-text("No thanks")',

            # Chat widgets
            '[class*="chat"] .close',
            '[class*="chat"] .minimize',
            '[id*="chat"] .close',

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
            '.btn-close'
        ]

        overlays_dismissed = 0
        for selector in overlay_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0 and await locator.is_visible():
                    await locator.click()
                    overlays_dismissed += 1
                    await asyncio.sleep(0.5)  # Brief pause after dismissal
                    print(f"      ✅ Dismissed overlay: {selector}")
            except Exception:
                continue

        print(f"   📊 Dismissed {overlays_dismissed} overlays")
        return overlays_dismissed

    async def streamlined_form_fill(self, page, field_selector: str, value: str, field_name: str) -> bool:
        """Streamlined form filling - faster but still human-like."""
        try:
            locator = page.locator(field_selector).first
            await locator.wait_for(timeout=4000)

            # Streamlined interaction (faster but still natural)
            await locator.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(0.2, 0.4))  # Reduced from 0.3-0.6

            # Focus and clear
            await locator.focus()
            await locator.fill("")
            await asyncio.sleep(random.uniform(0.1, 0.2))

            # Faster typing with occasional pauses
            chars = str(value)
            for i, char in enumerate(chars):
                await locator.type(char)

                # Streamlined typing speed
                if i % 5 == 0:  # Pause every 5 characters
                    delay = random.uniform(0.05, 0.10)
                else:
                    delay = random.uniform(0.02, 0.06)  # Faster overall

                await asyncio.sleep(delay)

            # Quick validation trigger
            await page.evaluate(f"document.querySelector('{field_selector}').blur()")
            await asyncio.sleep(random.uniform(0.1, 0.3))  # Reduced validation pause

            print(f"      ✅ {field_name}")
            return True

        except Exception as e:
            print(f"      ❌ {field_name}: {e}")
            return False

    async def handle_checkboxes(self, page) -> list:
        """Find and select all relevant checkboxes."""
        print("   ☑️  Handling checkboxes...")

        checked_boxes = []
        checkbox_selectors = [
            'input[type="checkbox"]',
            '[role="checkbox"]'
        ]

        for selector in checkbox_selectors:
            try:
                checkboxes = page.locator(selector)
                count = await checkboxes.count()

                for i in range(count):
                    checkbox = checkboxes.nth(i)

                    # Skip if already checked
                    if await checkbox.is_checked():
                        continue

                    # Get label text for context
                    try:
                        parent = checkbox.locator('xpath=..')
                        label_text = await parent.inner_text()
                        label_text = label_text.strip()[:50]  # First 50 chars
                    except:
                        label_text = "Unknown checkbox"

                    # Check relevant checkboxes (consent, agreement, etc.)
                    relevant_keywords = ['agree', 'consent', 'privacy', 'terms', 'contact', 'communication']
                    if any(keyword in label_text.lower() for keyword in relevant_keywords):
                        try:
                            await checkbox.check()
                            checked_boxes.append(label_text)
                            print(f"      ✅ Checked: {label_text}")
                            await asyncio.sleep(0.3)
                        except Exception as e:
                            print(f"      ❌ Failed to check: {label_text} - {e}")

            except Exception:
                continue

        return checked_boxes

    async def handle_dropdowns(self, page) -> dict:
        """Find and select relevant dropdown options."""
        print("   📋 Handling dropdowns...")

        dropdown_selections = {}

        try:
            selects = page.locator('select')
            count = await selects.count()

            for i in range(count):
                select = selects.nth(i)

                # Get dropdown label/context
                try:
                    select_id = await select.get_attribute('id')
                    name = await select.get_attribute('name')

                    # Find associated label
                    if select_id:
                        label = page.locator(f'label[for="{select_id}"]').first
                        if await label.count() > 0:
                            label_text = await label.inner_text()
                        else:
                            label_text = name or f"dropdown_{i}"
                    else:
                        label_text = name or f"dropdown_{i}"

                except:
                    label_text = f"dropdown_{i}"

                # Get options
                try:
                    options = select.locator('option')
                    option_count = await options.count()

                    if option_count <= 1:  # Skip if no real options
                        continue

                    # Smart option selection based on label
                    selected_option = None
                    label_lower = label_text.lower()

                    # Contact method preferences
                    if any(word in label_lower for word in ['contact', 'prefer', 'method', 'reach']):
                        preference_order = ['text', 'sms', 'phone', 'call', 'email']
                        for pref in preference_order:
                            for j in range(option_count):
                                option_text = await options.nth(j).inner_text()
                                if pref in option_text.lower():
                                    selected_option = option_text
                                    break
                            if selected_option:
                                break

                    # Interest/inquiry type
                    elif any(word in label_lower for word in ['interest', 'inquiry', 'reason', 'department']):
                        interest_keywords = ['sales', 'new', 'vehicle', 'lease', 'purchase']
                        for keyword in interest_keywords:
                            for j in range(option_count):
                                option_text = await options.nth(j).inner_text()
                                if keyword in option_text.lower():
                                    selected_option = option_text
                                    break
                            if selected_option:
                                break

                    # Default: select first non-empty option
                    if not selected_option:
                        for j in range(1, option_count):  # Skip first (usually empty)
                            option_text = await options.nth(j).inner_text()
                            if option_text.strip():
                                selected_option = option_text
                                break

                    # Make selection
                    if selected_option:
                        await select.select_option(label=selected_option)
                        dropdown_selections[label_text] = selected_option
                        print(f"      ✅ {label_text}: {selected_option}")
                        await asyncio.sleep(0.3)

                except Exception as e:
                    print(f"      ❌ Dropdown {label_text}: {e}")

        except Exception:
            pass

        return dropdown_selections

    async def force_submit(self, page) -> bool:
        """Force submit with multiple strategies."""
        print("   🚀 Attempting force submission...")

        # Strategy 1: Try multiple submit selectors
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            '.submit-button',
            '.gform_button',
            '[name*="submit"]'
        ]

        for selector in submit_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0:
                    print(f"      🎯 Trying: {selector}")

                    # Dismiss overlays first
                    await self.dismiss_overlays(page)

                    # Try normal click
                    try:
                        await locator.click(timeout=5000)
                        print(f"      ✅ Normal click successful")
                        return True
                    except:
                        pass

                    # Try force click
                    try:
                        await locator.click(force=True, timeout=5000)
                        print(f"      ✅ Force click successful")
                        return True
                    except:
                        pass

            except:
                continue

        # Strategy 2: JavaScript submission
        print("      🔧 Trying JavaScript form submission...")
        try:
            # Find form and submit via JavaScript
            result = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    for (let form of forms) {
                        if (form.querySelector('input[type="email"], input[name*="email"]')) {
                            form.submit();
                            return 'javascript_submit_success';
                        }
                    }
                    return 'no_form_found';
                }
            """)

            if result == 'javascript_submit_success':
                print(f"      ✅ JavaScript submission successful")
                return True

        except Exception as e:
            print(f"      ❌ JavaScript submission failed: {e}")

        return False

    async def test_complete_end_to_end(self):
        """Complete end-to-end test with random dealership."""
        print("🎯 COMPLETE END-TO-END SUBMISSION TEST")
        print("🔥 Random Dealership + Full Form + Overlays + Confirmation")
        print("=" * 75)

        # Get random dealership
        dealership = self.get_random_dealership()

        print(f"🏢 Selected Dealership:")
        print(f"   📛 Name: {dealership['name']}")
        print(f"   🔗 Website: {dealership['website']}")
        print(f"   📍 Location: {dealership['city']}, {dealership['state']}")
        print(f"   📞 Phone: {dealership.get('phone', 'N/A')}")
        print("=" * 75)

        stealth = CloudflareStealth()
        browser = None
        context = None

        try:
            print(f"\n🚀 Phase 1: Stealth Browser & Navigation")
            browser, context, page = await stealth.create_stealth_session()

            nav_success = await stealth.navigate_with_cloudflare_evasion(page, dealership['website'])
            if not nav_success:
                print("   ❌ Navigation failed")
                return

            print("   ✅ Navigation successful")

            # Initial overlay dismissal
            await self.dismiss_overlays(page)

            print(f"\n📝 Phase 2: Form Detection")
            detector = EnhancedFormDetector()
            form_result = await detector.detect_contact_form(page)

            if not form_result.success:
                print("   ❌ Form detection failed")
                return

            print(f"   ✅ Form detected - {len(form_result.fields)} fields")

            print(f"\n✍️  Phase 3: Streamlined Form Filling")
            filled_count = 0
            field_order = ['first_name', 'last_name', 'email', 'phone', 'zip', 'message']

            for field_name in field_order:
                if field_name in form_result.fields and field_name in self.test_data:
                    field = form_result.fields[field_name]
                    success = await self.streamlined_form_fill(
                        page, field.selector, self.test_data[field_name], field_name
                    )
                    if success:
                        filled_count += 1

                    # Reduced pause between fields
                    await asyncio.sleep(random.uniform(0.3, 0.8))

            print(f"   📊 Fields filled: {filled_count}/{len(form_result.fields)}")

            print(f"\n☑️  Phase 4: Checkboxes & Dropdowns")
            checked_boxes = await self.handle_checkboxes(page)
            dropdown_selections = await self.handle_dropdowns(page)

            print(f"   📊 Checkboxes: {len(checked_boxes)}")
            print(f"   📊 Dropdowns: {len(dropdown_selections)}")

            # Pre-submission screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_screenshot = f"complete_e2e_pre_{timestamp}.png"
            await page.screenshot(path=pre_screenshot, full_page=True)
            print(f"   📸 Pre-submission: {pre_screenshot}")

            print(f"\n📤 Phase 5: Complete Submission")

            # Final overlay dismissal before submission
            await self.dismiss_overlays(page)

            # Brief review pause
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Force submission
            submission_success = await self.force_submit(page)

            if submission_success:
                print("   ✅ Form submitted successfully!")
            else:
                print("   ❌ Form submission failed")

            print(f"\n📊 Phase 6: Confirmation Analysis")

            # Wait for page response
            await asyncio.sleep(5)

            # Post-submission screenshot
            post_screenshot = f"complete_e2e_post_{timestamp}.png"
            await page.screenshot(path=post_screenshot, full_page=True)
            print(f"   📸 Post-submission: {post_screenshot}")

            # Analyze results
            current_url = page.url
            page_title = await page.title()
            body_text = await page.inner_text('body')

            print(f"   🔗 Current URL: {current_url}")
            print(f"   📄 Page Title: {page_title}")

            # Check for success indicators
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
                'submitted successfully'
            ]

            success_found = []
            for pattern in success_patterns:
                if pattern in body_text.lower():
                    success_found.append(pattern)

            # Check for blocking
            blocked_indicators = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'access denied',
                'security block'
            ]

            blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)

            print(f"\n🏆 FINAL END-TO-END RESULT:")
            if blocked:
                print("   🚨 BLOCKED - Cloudflare detected automation")
            elif success_found:
                print("   🎉 SUCCESS - Submission confirmed!")
                for pattern in success_found:
                    print(f"      ✅ Found: '{pattern}'")
            elif submission_success:
                print("   ✅ LIKELY SUCCESS - Form submitted, checking page content")
                print(f"      📄 Page preview: {body_text[:200]}...")
            else:
                print("   ⚠️  UNCLEAR - No clear success confirmation")

            print(f"\n📋 Summary:")
            print(f"   🏢 Dealership: {dealership['name']}")
            print(f"   📝 Fields: {filled_count} filled")
            print(f"   ☑️  Checkboxes: {len(checked_boxes)} selected")
            print(f"   📋 Dropdowns: {len(dropdown_selections)} set")
            print(f"   📤 Submitted: {'Yes' if submission_success else 'No'}")

            # Keep browser open for visual confirmation
            print(f"\n👁️  VISUAL CONFIRMATION - 15 SECONDS")
            print("   👀 Check browser for confirmation messages!")

            for i in range(15, 0, -1):
                print(f"   ⏱️  {i}s...")
                await asyncio.sleep(1)

            print(f"\n📸 Screenshots:")
            print(f"   📷 Before: {pre_screenshot}")
            print(f"   📷 After: {post_screenshot}")

        except Exception as e:
            print(f"\n💥 Test failed: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print(f"\n🧹 Cleanup...")
            await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 COMPLETE END-TO-END SUBMISSION TEST")
    print("📋 Random dealership, full form, checkboxes, overlays, confirmation")
    print("🎯 Goal: Actual successful submission with confirmation message")
    print("👀 Browser stays open 15 seconds for visual confirmation\n")

    try:
        tester = CompleteEndToEndTester()
        await tester.test_complete_end_to_end()
        print("\n🏁 Complete end-to-end test finished!")

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as exc:
        print(f"\n💥 Failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())