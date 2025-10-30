#!/usr/bin/env python3
"""
FIXED: Comprehensive Test with Proper Form Filling

Fixes:
1. Fill ALL fields (first name, last name, email, phone, zip, message)
2. Check consent checkboxes
3. Better success detection
4. Log ALL errors for debugging
"""

import asyncio
import json
import csv
import random
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.browser.dealerinspire_bypass import apply_dealerinspire_bypass


class FixedDealershipTester:
    """Test dealerships with FIXED comprehensive form filling"""

    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()
        self.results = []

        # Test user information
        self.test_user = {
            'first_name': 'Miguel',
            'last_name': 'Montoya',
            'email': 'migueljmontoya@protonmail.com',
            'phone': '6503320719',
            'zip_code': '90066',
            'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel'
        }

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"tests/fixed_test_{timestamp}")
        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*80}")
        print(f"FIXED DEALERSHIP SUBMISSION TEST")
        print(f"{'='*80}")
        print(f"📁 Output: {self.output_dir}")
        print(f"👤 Test User: {self.test_user['first_name']} {self.test_user['last_name']}")
        print(f"📧 Email: {self.test_user['email']}")
        print(f"🔢 Testing: 20 random dealerships")
        print(f"⏰ Started: {datetime.now()}")
        print(f"{'='*80}\n")

    def load_random_dealerships(self, count=20):
        """Load random dealerships from CSV, excluding Autonation"""
        dealerships = []

        with open('Dealerships - Jeep.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_dealers = [row for row in reader
                          if row.get('website') and
                          'autonation' not in row.get('dealer_name', '').lower()]

        # Select random sample
        selected = random.sample(all_dealers, min(count, len(all_dealers)))

        for i, dealer in enumerate(selected, 1):
            dealerships.append({
                'index': i,
                'dealer_name': dealer['dealer_name'],
                'website': dealer['website'],
            })

        return dealerships

    async def detect_contact_form(self, page, dealer_name, website):
        """Detect contact form and take screenshot"""

        print(f"   🔍 Step 1: Detecting contact form...")

        try:
            # Navigate with DealerInspire bypass if needed
            if 'dealerinspire' in website.lower():
                print(f"      🔍 DealerInspire detected - using bypass")
                await apply_dealerinspire_bypass(page, website)
            else:
                await page.goto(website, wait_until='domcontentloaded', timeout=30000)

            await asyncio.sleep(2)

            # Look for contact links
            contact_links = []
            patterns = ['a:has-text("Contact")', 'a[href*="contact"]', 'a:has-text("Get Quote")']

            for pattern in patterns:
                try:
                    links = await page.locator(pattern).all()
                    for link in links[:3]:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()
                        if href and href not in ['#', 'javascript:void(0)']:
                            contact_links.append({'href': href, 'text': text})
                except Exception as e:
                    print(f"      ⚠️  Error finding contact links: {e}")

            # Visit first contact link if found
            if contact_links:
                href = contact_links[0]['href']
                if href.startswith('/'):
                    full_url = website.rstrip('/') + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = None

                if full_url:
                    print(f"      🔗 Visiting contact page: {full_url}")

                    if 'dealerinspire' in full_url.lower():
                        await apply_dealerinspire_bypass(page, full_url)
                    else:
                        await page.goto(full_url, wait_until='domcontentloaded', timeout=20000)

                    await asyncio.sleep(2)

            # Check for forms
            forms = await page.locator('form').all()

            if len(forms) == 0:
                print(f"      ❌ No forms found")
                return None, None

            print(f"      ✅ Found {len(forms)} forms")

            # Take screenshot of form
            screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_1_form_detected.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"      📸 Screenshot saved: {screenshot_name}")

            return page.url, str(screenshot_path)

        except Exception as e:
            print(f"      ❌ Error: {e}")
            return None, None

    async def fill_single_field(self, page, field_selectors, value, field_name):
        """Try to fill a single field with multiple selector strategies"""
        for selector in field_selectors:
            try:
                elements = await page.locator(selector).all()
                for elem in elements:
                    if await elem.is_visible() and await elem.is_editable():
                        await elem.fill(value)
                        print(f"         ✅ Filled {field_name}: {value}")
                        return True
            except Exception as e:
                print(f"         ⚠️  Failed selector {selector} for {field_name}: {e}")
                continue
        return False

    async def fill_form_completely(self, page, dealer_name):
        """Fill ALL form fields comprehensively"""

        print(f"   ✏️  Step 2: Filling form completely...")

        try:
            filled_fields = []

            # EMAIL - highest priority
            email_selectors = [
                'input[type="email"]',
                'input[name*="email" i]',
                'input[id*="email" i]',
                'input[placeholder*="email" i]',
            ]
            if await self.fill_single_field(page, email_selectors, self.test_user['email'], 'email'):
                filled_fields.append('email')
            else:
                print(f"         ❌ Could not fill email field")

            # FIRST NAME
            first_name_selectors = [
                'input[name*="first" i][name*="name" i]',
                'input[id*="first" i]',
                'input[placeholder*="first" i]',
                'input[name="input_1"]',  # Gravity Forms pattern
                'input[name="input_2"]',  # Sometimes first name is input_2
            ]
            if await self.fill_single_field(page, first_name_selectors, self.test_user['first_name'], 'first name'):
                filled_fields.append('first_name')
            else:
                print(f"         ⚠️  Could not fill first name field")

            # LAST NAME
            last_name_selectors = [
                'input[name*="last" i][name*="name" i]',
                'input[id*="last" i]',
                'input[placeholder*="last" i]',
                'input[name="input_2"]',  # Gravity Forms pattern
                'input[name="input_3"]',  # Sometimes last name is input_3
            ]
            if await self.fill_single_field(page, last_name_selectors, self.test_user['last_name'], 'last name'):
                filled_fields.append('last_name')
            else:
                print(f"         ⚠️  Could not fill last name field")

            # PHONE
            phone_selectors = [
                'input[type="tel"]',
                'input[name*="phone" i]',
                'input[id*="phone" i]',
                'input[placeholder*="phone" i]',
                'input[name="input_3"]',  # Gravity Forms
                'input[name="input_4"]',
            ]
            if await self.fill_single_field(page, phone_selectors, self.test_user['phone'], 'phone'):
                filled_fields.append('phone')
            else:
                print(f"         ⚠️  Could not fill phone field")

            # ZIP CODE
            zip_selectors = [
                'input[name*="zip" i]',
                'input[id*="zip" i]',
                'input[name*="postal" i]',
                'input[placeholder*="zip" i]',
                'input[name="input_5"]',  # Gravity Forms
                'input[name="input_6"]',
            ]
            if await self.fill_single_field(page, zip_selectors, self.test_user['zip_code'], 'zip code'):
                filled_fields.append('zip_code')
            else:
                print(f"         ⚠️  Could not fill zip code field")

            # MESSAGE/COMMENTS
            message_selectors = [
                'textarea',
                'textarea[name*="message" i]',
                'textarea[name*="comment" i]',
                'textarea[id*="message" i]',
                'textarea[name="input_8"]',  # Gravity Forms
                'textarea[name="input_10"]',
            ]
            if await self.fill_single_field(page, message_selectors, self.test_user['message'], 'message'):
                filled_fields.append('message')
            else:
                print(f"         ⚠️  Could not fill message field")

            # CHECK CONSENT CHECKBOXES (CRITICAL!)
            checkbox_selectors = [
                'input[type="checkbox"]',
                'input[name*="consent" i]',
                'input[name*="agree" i]',
                'input[id*="consent" i]',
            ]

            checkboxes_checked = 0
            for selector in checkbox_selectors:
                try:
                    checkboxes = await page.locator(selector).all()
                    for checkbox in checkboxes:
                        if await checkbox.is_visible() and not await checkbox.is_checked():
                            await checkbox.check()
                            checkboxes_checked += 1
                            print(f"         ✅ Checked consent checkbox")
                except Exception as e:
                    print(f"         ⚠️  Checkbox error: {e}")

            print(f"\n      📊 Summary: Filled {len(filled_fields)} fields: {', '.join(filled_fields)}")
            print(f"      📊 Checked {checkboxes_checked} checkboxes")

            if len(filled_fields) >= 3:  # At least 3 fields filled
                # Take screenshot BEFORE submission
                screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_2_form_filled.png"
                screenshot_path = self.screenshots_dir / screenshot_name
                await page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"      📸 Screenshot saved: {screenshot_name}")

                return True, str(screenshot_path), filled_fields
            else:
                print(f"      ❌ Insufficient fields filled ({len(filled_fields)}/6 minimum 3)")
                return False, None, filled_fields

        except Exception as e:
            print(f"      ❌ Error filling form: {e}")
            return False, None, []

    async def submit_form(self, page, dealer_name):
        """Submit form and verify success"""

        print(f"   🚀 Step 3: Submitting form...")

        try:
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Send")',
                'button:has-text("Let\'s Talk")',
                '.gform_button',
            ]

            submitted = False
            for selector in submit_selectors:
                try:
                    buttons = await page.locator(selector).all()
                    for button in buttons:
                        if await button.is_visible():
                            await button.click()
                            submitted = True
                            print(f"      ✅ Submit button clicked")
                            break
                    if submitted:
                        break
                except Exception as e:
                    print(f"      ⚠️  Submit selector failed {selector}: {e}")

            if not submitted:
                print(f"      ❌ Could not find/click submit button")
                return False, None

            # Wait for response
            await asyncio.sleep(4)

            # Take screenshot
            screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_3_submitted.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            await page.screenshot(path=str(screenshot_path), full_page=True)

            # IMPROVED success detection
            page_content = await page.content()
            page_text = await page.evaluate("() => document.body.innerText")

            # Look for SUCCESS indicators
            success_indicators = [
                'thank you',
                'thanks for',
                'received your',
                'submitted successfully',
                'we\'ll be in touch',
                'confirmation',
                'gform_confirmation_message',
                'message has been sent',
            ]

            # Look for ERROR indicators (these override success)
            error_indicators = [
                'field is required',
                'required field',
                'please enter',
                'invalid',
                'error',
                'must be filled',
                'this field is required',
                'gform_validation_error',
            ]

            has_errors = any(indicator in page_text.lower() for indicator in error_indicators)
            has_success = any(indicator in page_text.lower() for indicator in success_indicators)

            if has_errors:
                print(f"      ❌ SUBMISSION FAILED: Form validation errors detected")
                print(f"      📸 Screenshot saved: {screenshot_name}")
                return False, str(screenshot_path)
            elif has_success:
                print(f"      ✅ SUBMISSION SUCCESSFUL: Confirmation detected")
                print(f"      📸 Screenshot saved: {screenshot_name}")
                return True, str(screenshot_path)
            else:
                print(f"      ⚠️  UNCLEAR: No clear success or error message")
                print(f"      📸 Screenshot saved: {screenshot_name}")
                return False, str(screenshot_path)

        except Exception as e:
            print(f"      ❌ Error submitting: {e}")
            return False, None

    async def test_dealership(self, context, dealer):
        """Test a single dealership through all stages"""

        dealer_name = dealer['dealer_name']
        website = dealer['website']
        index = dealer['index']

        print(f"\n{'='*80}")
        print(f"🏪 #{index:02d}: {dealer_name}")
        print(f"🌐 URL: {website}")
        print(f"{'='*80}")

        result = {
            'index': index,
            'dealer_name': dealer_name,
            'website': website,
            'form_detected': False,
            'form_filled': False,
            'form_submitted': False,
            'fields_filled': [],
            'contact_url': None,
            'screenshot_detected': None,
            'screenshot_filled': None,
            'screenshot_submitted': None,
            'error': None,
        }

        page = await self.browser_manager.create_enhanced_stealth_page(context)

        try:
            # Stage 1: Detect form
            contact_url, screenshot_detected = await self.detect_contact_form(page, dealer_name, website)

            if contact_url:
                result['form_detected'] = True
                result['contact_url'] = contact_url
                result['screenshot_detected'] = screenshot_detected

                # Stage 2: Fill form COMPLETELY
                filled, screenshot_filled, fields = await self.fill_form_completely(page, dealer_name)

                if filled:
                    result['form_filled'] = True
                    result['screenshot_filled'] = screenshot_filled
                    result['fields_filled'] = fields

                    # Stage 3: Submit form
                    submitted, screenshot_submitted = await self.submit_form(page, dealer_name)

                    if submitted:
                        result['form_submitted'] = True
                        result['screenshot_submitted'] = screenshot_submitted
                        print(f"\n   ✅ FULL SUCCESS: Detected → Filled ({len(fields)} fields) → Submitted")
                    else:
                        result['screenshot_submitted'] = screenshot_submitted
                        print(f"\n   ❌ FAILED: Detected → Filled → Submission failed/unclear")
                else:
                    print(f"\n   ❌ FAILED: Detected but could not fill enough fields")
            else:
                print(f"\n   ❌ FAILED: No contact form detected")
                result['error'] = "No contact form found"

        except Exception as e:
            print(f"\n   ❌ ERROR: {e}")
            result['error'] = str(e)

        finally:
            await page.close()

        self.results.append(result)
        return result

    async def run_all_tests(self):
        """Run tests on 20 random dealerships"""

        dealerships = self.load_random_dealerships(20)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await self.browser_manager.create_enhanced_stealth_context(browser)

            for dealer in dealerships:
                await self.test_dealership(context, dealer)

            await context.close()
            await browser.close()

        # Save results and print summary
        self._save_results()
        self._print_summary()

    def _save_results(self):
        """Save results to JSON and CSV"""

        # Save JSON
        json_path = self.output_dir / "results.json"
        with open(json_path, 'w') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'total_dealerships': len(self.results),
                'results': self.results,
            }, f, indent=2)

        # Save CSV
        csv_path = self.output_dir / "results.csv"
        with open(csv_path, 'w', newline='') as f:
            fieldnames = ['index', 'dealer_name', 'website', 'form_detected', 'form_filled',
                         'form_submitted', 'fields_filled', 'contact_url', 'screenshot_detected',
                         'screenshot_filled', 'screenshot_submitted', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.results:
                r_copy = r.copy()
                r_copy['fields_filled'] = ','.join(r_copy['fields_filled'])
                writer.writerow(r_copy)

        print(f"\n💾 Results saved:")
        print(f"   - JSON: {json_path}")
        print(f"   - CSV: {csv_path}")

    def _print_summary(self):
        """Print comprehensive summary table"""

        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")

        total = len(self.results)
        detected = len([r for r in self.results if r['form_detected']])
        filled = len([r for r in self.results if r['form_filled']])
        submitted = len([r for r in self.results if r['form_submitted']])

        print(f"\n📊 Overall Statistics:")
        print(f"   Total dealerships tested: {total}")
        print(f"   ✅ Forms detected: {detected}/{total} ({detected/total*100:.1f}%)")
        print(f"   ✏️  Forms filled: {filled}/{total} ({filled/total*100:.1f}%)")
        print(f"   🚀 Forms submitted: {submitted}/{total} ({submitted/total*100:.1f}%)")

        print(f"\n📋 Detailed Results Table:")
        print(f"{'='*80}")
        print(f"{'#':<4} {'Dealer Name':<35} {'Detect':<8} {'Fill':<8} {'Submit':<8}")
        print(f"{'='*80}")

        for r in self.results:
            detect_icon = '✅' if r['form_detected'] else '❌'
            fill_icon = '✅' if r['form_filled'] else ('⚠️' if r['form_detected'] else '❌')
            submit_icon = '✅' if r['form_submitted'] else ('❌' if r['form_filled'] else '❌')

            dealer_name = r['dealer_name'][:33]

            print(f"{r['index']:<4} {dealer_name:<35} {detect_icon:<8} {fill_icon:<8} {submit_icon:<8}")

        print(f"{'='*80}")

        # Field fill analysis
        print(f"\n📊 Field Filling Analysis:")
        field_counts = {}
        for r in self.results:
            if r['form_filled']:
                for field in r['fields_filled']:
                    field_counts[field] = field_counts.get(field, 0) + 1

        for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
            print(f"   - {field}: {count}/{filled} forms")


async def main():
    """Main entry point"""
    tester = FixedDealershipTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
