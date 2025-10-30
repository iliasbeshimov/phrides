#!/usr/bin/env python3
"""
Enhanced submission test focused on avoiding detection during form submission.
Implements additional human behaviors specifically around the submission phase.
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


class EnhancedSubmissionTester:
    """Test with enhanced submission behaviors to avoid detection."""

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
        """Get a random dealership with valid website from CSV."""
        try:
            with open('Dealerships.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                valid_dealers = []

                for row in reader:
                    website = row.get('website', '').strip()
                    dealer_name = row.get('dealer_name', '').strip()

                    if website and website not in ['', 'N/A', 'None'] and website.startswith('http'):
                        # Skip sites we know have issues
                        if 'capcitycdjr.com' not in website:  # Skip our test site
                            valid_dealers.append({
                                'name': dealer_name,
                                'website': website,
                                'city': row.get('city', ''),
                                'state': row.get('state', ''),
                                'phone': row.get('phone', '')
                            })

                if valid_dealers:
                    return random.choice(valid_dealers)

        except Exception as e:
            print(f"Error reading CSV: {e}")

        # Fallback to a known working site for testing
        return {
            'name': 'Capital City CDJR (Fallback Test)',
            'website': 'https://www.capcitycdjr.com/contact-us/',
            'city': 'Jefferson City',
            'state': 'MO',
            'phone': '573-635-6137'
        }

    async def enhanced_human_form_fill(self, page, field_selector: str, value: str, field_name: str) -> bool:
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

    async def enhanced_human_submission(self, page, submit_selector: str) -> bool:
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
            await asyncio.sleep(random.uniform(2.0, 4.0))

            # 7. Click submit button
            print("   📤 Clicking submit button...")
            await submit_locator.click()

            # 8. Post-click wait for processing
            print("   ⏳ Waiting for form processing...")
            await asyncio.sleep(random.uniform(2.0, 4.0))

            return True

        except Exception as e:
            print(f"   ❌ Enhanced submission failed: {e}")
            return False

    async def test_enhanced_submission(self):
        """Run enhanced submission test with new dealership."""
        print("🎯 ENHANCED SUBMISSION TEST")
        print("🔥 Focus: Avoiding Detection During Form Submission")
        print("=" * 70)

        # Get random dealership
        dealership = self.get_random_dealership()

        print(f"🎲 Selected Random Dealership:")
        print(f"   🏢 Name: {dealership['name']}")
        print(f"   🔗 Website: {dealership['website']}")
        print(f"   📍 Location: {dealership['city']}, {dealership['state']}")
        print(f"   📞 Phone: {dealership.get('phone', 'N/A')}")
        print("=" * 70)

        print(f"\n📋 Test Data:")
        print(f"   👤 Name: {self.test_data['first_name']} {self.test_data['last_name']}")
        print(f"   📧 Email: {self.test_data['email']}")
        print(f"   📞 Phone: {self.test_data['phone']}")
        print(f"   📮 Zip: {self.test_data['zip_code']}")
        print(f"   💬 Message: {self.test_data['message'][:50]}...")

        stealth = CloudflareStealth()
        browser = None
        context = None

        try:
            print(f"\n🚀 Phase 1: Enhanced Stealth Browser Setup")
            browser, context, page = await stealth.create_stealth_session()
            print("   ✅ Cloudflare stealth browser ready")

            print(f"\n🌐 Phase 2: Navigation with Cloudflare Evasion")
            print("   ⚠️  BROWSER WILL OPEN - Watch the enhanced automation")
            nav_success = await stealth.navigate_with_cloudflare_evasion(
                page, dealership['website']
            )

            if not nav_success:
                print("   ❌ Navigation failed - Cloudflare blocked")
                return

            print("   ✅ Navigation successful - Cloudflare bypassed")

            print(f"\n📝 Phase 3: Enhanced Form Detection")
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
                if field_name in form_result.fields and field_name in self.test_data:
                    field = form_result.fields[field_name]
                    print(f"\n   📝 Filling {field_name.replace('_', ' ').title()}:")

                    success = await self.enhanced_human_form_fill(
                        page, field.selector, self.test_data[field_name], field_name
                    )

                    if success:
                        filled_count += 1
                        print(f"      ✅ {field_name.replace('_', ' ').title()} completed")
                    else:
                        print(f"      ❌ {field_name.replace('_', ' ').title()} failed")

                    # Natural pause between fields
                    await asyncio.sleep(random.uniform(0.8, 2.0))

            print(f"\n   📊 Fields filled: {filled_count}/{len(form_result.fields)}")

            if filled_count == 0:
                print("   ❌ No fields filled - aborting test")
                return

            # Take screenshot before submission
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_submit_screenshot = f"enhanced_pre_submit_{timestamp}.png"
            await page.screenshot(path=pre_submit_screenshot, full_page=True)
            print(f"   📸 Pre-submission screenshot: {pre_submit_screenshot}")

            print(f"\n📤 Phase 5: Enhanced Submission with Anti-Detection")

            # Find submit button
            submit_selector = None
            if hasattr(form_result, 'submit_button') and form_result.submit_button:
                submit_selector = form_result.submit_button.get('selector')

            if not submit_selector:
                # Fallback submit detection
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")',
                    '.submit-button'
                ]

                for selector in submit_selectors:
                    if await page.locator(selector).count() > 0:
                        submit_selector = selector
                        break

            if not submit_selector:
                print("   ❌ No submit button found")
                return

            print(f"   🎯 Submit button found: {submit_selector}")

            # Enhanced submission with anti-detection behaviors
            submission_success = await self.enhanced_human_submission(page, submit_selector)

            if submission_success:
                print("   ✅ Form submitted with enhanced human behaviors")
            else:
                print("   ❌ Enhanced submission failed")

            print(f"\n📊 Phase 6: Results Analysis")

            # Wait longer to see response
            print("   ⏳ Waiting for server response...")
            await asyncio.sleep(5)

            # Take post-submission screenshot
            post_submit_screenshot = f"enhanced_post_submit_{timestamp}.png"
            await page.screenshot(path=post_submit_screenshot, full_page=True)
            print(f"   📸 Post-submission screenshot: {post_submit_screenshot}")

            # Check for blocking indicators
            body_text = await page.inner_text('body')
            blocked_indicators = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'blocked because your browser',
                'access denied',
                'why have i been blocked'
            ]

            blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)

            if blocked:
                print("   ❌ BLOCKED - Detected blocking page after submission")
                print(f"   🔍 Page content preview: {body_text[:200]}...")
            else:
                print("   ✅ NO BLOCKING DETECTED - Submission appears successful")

            # Look for success indicators
            success_patterns = [
                'thank you',
                'we will be in touch',
                'submission received',
                'successfully sent',
                'we have received',
                'your message has been sent'
            ]

            success_detected = any(pattern in body_text.lower() for pattern in success_patterns)

            if success_detected:
                print("   🎉 SUCCESS CONFIRMATION DETECTED!")
                for pattern in success_patterns:
                    if pattern in body_text.lower():
                        print(f"      ✅ Found: '{pattern}'")
            else:
                print("   ⚠️  No clear success confirmation found")

            print(f"\n🏆 FINAL RESULT:")
            if not blocked and success_detected:
                print("   🎉 COMPLETE SUCCESS - Form submitted without detection!")
            elif not blocked:
                print("   ✅ PARTIAL SUCCESS - No blocking, unclear confirmation")
            else:
                print("   ❌ SUBMISSION BLOCKED - Cloudflare detected automation")

            # Keep browser open for manual inspection
            print(f"\n👁️  KEEPING BROWSER OPEN FOR 10 SECONDS FOR VISUAL CONFIRMATION")
            print("   👀 Check the browser window for success/error messages")
            print("   📋 Look for confirmation pages, thank you messages, etc.")

            for i in range(10, 0, -1):
                print(f"   ⏱️  {i} seconds remaining...")
                await asyncio.sleep(1)

        except Exception as e:
            print(f"\n💥 Test failed: {e}")
            import traceback
            traceback.print_exc()

        finally:
            print(f"\n🧹 Cleaning up...")
            await stealth.close_session(browser, context)


async def main():
    """Main execution."""
    print("🔧 STARTING ENHANCED SUBMISSION TEST...")
    print("📋 Testing anti-detection behaviors during form submission")
    print("👀 Browser will stay open for 10 seconds after submission")
    print("⏸️  Press Ctrl+C to stop\n")

    try:
        tester = EnhancedSubmissionTester()
        await tester.test_enhanced_submission()
        print("\n🏁 Enhanced submission test complete!")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())