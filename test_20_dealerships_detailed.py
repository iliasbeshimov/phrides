#!/usr/bin/env python3
"""
Comprehensive Test: 20 Random Dealerships with Detailed Screenshot Tracking

This test tracks 3 key stages:
1. Contact form detection (screenshot of detected form)
2. Form filling (screenshot after filling, before submission)
3. Successful submission (screenshot of confirmation message)
"""

import asyncio
import json
import csv
import random
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.browser.dealerinspire_bypass import apply_dealerinspire_bypass, DealerInspireBypass


class DetailedDealershipTester:
    """Test dealerships with detailed screenshot tracking at each stage"""

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
        self.output_dir = Path(f"tests/detailed_test_{timestamp}")
        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*80}")
        print(f"DETAILED DEALERSHIP SUBMISSION TEST")
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
                except:
                    pass

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
            gravity_forms = await page.locator('.gform_wrapper').count()

            if len(forms) == 0:
                print(f"      ❌ No forms found")
                return None, None

            print(f"      ✅ Found {len(forms)} forms ({gravity_forms} Gravity Forms)")

            # Take screenshot of form
            screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_1_form_detected.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"      📸 Screenshot saved: {screenshot_name}")

            return page.url, str(screenshot_path)

        except Exception as e:
            print(f"      ❌ Error: {e}")
            return None, None

    async def fill_form(self, page, dealer_name):
        """Fill form with test data and take screenshot before submission"""

        print(f"   ✏️  Step 2: Filling form...")

        try:
            # Check for Gravity Forms first (most common)
            gravity_form = await page.locator('.gform_wrapper').count()

            if gravity_form > 0:
                print(f"      📋 Filling Gravity Form...")

                # Find and fill fields
                filled_fields = []

                # Email
                email_selectors = ['input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]']
                for selector in email_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0 and await elem.is_visible():
                            await elem.fill(self.test_user['email'])
                            filled_fields.append('email')
                            break
                    except:
                        pass

                # First name
                name_selectors = ['input[name*="first" i]', 'input[id*="first" i]', 'input[placeholder*="first" i]']
                for selector in name_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0 and await elem.is_visible():
                            await elem.fill(self.test_user['first_name'])
                            filled_fields.append('first_name')
                            break
                    except:
                        pass

                # Last name
                last_selectors = ['input[name*="last" i]', 'input[id*="last" i]', 'input[placeholder*="last" i]']
                for selector in last_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0 and await elem.is_visible():
                            await elem.fill(self.test_user['last_name'])
                            filled_fields.append('last_name')
                            break
                    except:
                        pass

                # Phone
                phone_selectors = ['input[name*="phone" i]', 'input[id*="phone" i]', 'input[type="tel"]']
                for selector in phone_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0 and await elem.is_visible():
                            await elem.fill(self.test_user['phone'])
                            filled_fields.append('phone')
                            break
                    except:
                        pass

                # Message
                message_selectors = ['textarea', 'textarea[name*="message" i]', 'textarea[name*="comment" i]']
                for selector in message_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.count() > 0 and await elem.is_visible():
                            await elem.fill(self.test_user['message'])
                            filled_fields.append('message')
                            break
                    except:
                        pass

                if len(filled_fields) >= 2:  # At least email + one other field
                    print(f"      ✅ Filled {len(filled_fields)} fields: {', '.join(filled_fields)}")

                    # Take screenshot BEFORE submission
                    screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_2_form_filled.png"
                    screenshot_path = self.screenshots_dir / screenshot_name
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"      📸 Screenshot saved: {screenshot_name}")

                    return True, str(screenshot_path)
                else:
                    print(f"      ⚠️  Only filled {len(filled_fields)} fields - insufficient")
                    return False, None

            else:
                # Generic form filling
                print(f"      📋 Filling generic form...")

                filled = False

                # Try to fill email
                try:
                    email_input = page.locator('input[type="email"]').first
                    if await email_input.count() > 0:
                        await email_input.fill(self.test_user['email'])
                        filled = True
                except:
                    pass

                # Try to fill textarea
                try:
                    textarea = page.locator('textarea').first
                    if await textarea.count() > 0:
                        await textarea.fill(self.test_user['message'])
                        filled = True
                except:
                    pass

                if filled:
                    screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_2_form_filled.png"
                    screenshot_path = self.screenshots_dir / screenshot_name
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    print(f"      ✅ Form filled")
                    print(f"      📸 Screenshot saved: {screenshot_name}")
                    return True, str(screenshot_path)
                else:
                    print(f"      ❌ Could not fill form")
                    return False, None

        except Exception as e:
            print(f"      ❌ Error filling form: {e}")
            return False, None

    async def submit_form(self, page, dealer_name):
        """Submit form and take screenshot of confirmation"""

        print(f"   🚀 Step 3: Submitting form...")

        try:
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Send")',
                '.gform_button',
            ]

            submitted = False
            for selector in submit_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.count() > 0 and await button.is_visible():
                        await button.click()
                        submitted = True
                        print(f"      ✅ Submit button clicked")
                        break
                except:
                    pass

            if not submitted:
                print(f"      ❌ Could not find submit button")
                return False, None

            # Wait for confirmation
            await asyncio.sleep(3)

            # Check for success indicators
            page_content = await page.content()
            success_indicators = [
                'thank you',
                'success',
                'received',
                'submitted',
                'confirmation',
                'gform_confirmation_message',
            ]

            is_success = any(indicator in page_content.lower() for indicator in success_indicators)

            # Take screenshot of confirmation
            screenshot_name = f"{dealer_name.lower().replace(' ', '_')[:30]}_3_submitted.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            await page.screenshot(path=str(screenshot_path), full_page=True)

            if is_success:
                print(f"      ✅ Submission successful!")
                print(f"      📸 Screenshot saved: {screenshot_name}")
                return True, str(screenshot_path)
            else:
                print(f"      ⚠️  Submission unclear (no confirmation detected)")
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

                # Stage 2: Fill form
                filled, screenshot_filled = await self.fill_form(page, dealer_name)

                if filled:
                    result['form_filled'] = True
                    result['screenshot_filled'] = screenshot_filled

                    # Stage 3: Submit form
                    submitted, screenshot_submitted = await self.submit_form(page, dealer_name)

                    if submitted:
                        result['form_submitted'] = True
                        result['screenshot_submitted'] = screenshot_submitted
                        print(f"\n   ✅ FULL SUCCESS: Detected → Filled → Submitted")
                    else:
                        print(f"\n   ⚠️  PARTIAL SUCCESS: Detected → Filled → Submission unclear")
                else:
                    print(f"\n   ⚠️  PARTIAL SUCCESS: Detected but could not fill")
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
                         'form_submitted', 'contact_url', 'screenshot_detected',
                         'screenshot_filled', 'screenshot_submitted', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

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
            submit_icon = '✅' if r['form_submitted'] else ('⚠️' if r['form_filled'] else '❌')

            dealer_name = r['dealer_name'][:33]

            print(f"{r['index']:<4} {dealer_name:<35} {detect_icon:<8} {fill_icon:<8} {submit_icon:<8}")

        print(f"{'='*80}")

        # Screenshot summary
        print(f"\n📸 Screenshots captured:")
        detected_screenshots = len([r for r in self.results if r['screenshot_detected']])
        filled_screenshots = len([r for r in self.results if r['screenshot_filled']])
        submitted_screenshots = len([r for r in self.results if r['screenshot_submitted']])

        print(f"   - Form detected: {detected_screenshots} screenshots")
        print(f"   - Form filled: {filled_screenshots} screenshots")
        print(f"   - Form submitted: {submitted_screenshots} screenshots")
        print(f"   - Total: {detected_screenshots + filled_screenshots + submitted_screenshots} screenshots")
        print(f"   - Location: {self.screenshots_dir}")


async def main():
    """Main entry point"""
    tester = DetailedDealershipTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
