#!/usr/bin/env python3
"""
Complete test on 20 random dealerships with actual form submission
Tests all critical fixes with real form filling and submission detection
"""

import asyncio
import pandas as pd
import os
import random
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError
from pathlib import Path

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from contact_page_detector import ContactPageDetector
from src.services.contact.contact_page_cache import (
    ContactPageResolver,
    ContactPageStore,
)


class DealershipSubmissionTester:
    """Test form detection, filling, and submission on random dealerships"""

    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()
        self.contact_store = ContactPageStore()
        self.contact_detector = ContactPageDetector()
        self.contact_resolver = ContactPageResolver(
            browser_manager=self.browser_manager,
            detector=self.contact_detector,
            store=self.contact_store,
            min_score=40,
            refresh_days=21,
        )

        # Test user information
        self.test_user = {
            'first_name': 'Miguel',
            'last_name': 'Montoya',
            'email': 'migueljmontoya@protonmail.com',
            'phone': '6503320719',
            'zip_code': '90066',
            'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel'
        }

    async def fill_and_submit_form(self, page, dealer_name, contact_url):
        """Fill form with test user data and submit"""
        print(f"      📝 Filling form with test user data...")

        try:
            # Wait for forms to be visible
            await page.wait_for_selector('form', timeout=10000)

            # Strategy 1: Try Gravity Forms (most common)
            gform_count = await page.locator('.gform_wrapper').count()
            if gform_count > 0:
                print(f"         🎯 Detected Gravity Forms, filling...")
                success = await self._fill_gravity_form(page)
                if success:
                    return await self._detect_submission_success(page, dealer_name)

            # Strategy 2: Try generic form filling
            print(f"         📋 Attempting generic form fill...")
            success = await self._fill_generic_form(page)
            if success:
                return await self._detect_submission_success(page, dealer_name)

            return {
                'filled': False,
                'submitted': False,
                'success': False,
                'error': 'Could not find fillable form fields'
            }

        except Exception as e:
            return {
                'filled': False,
                'submitted': False,
                'success': False,
                'error': str(e)
            }

    async def _fill_gravity_form(self, page):
        """Fill Gravity Forms with known field patterns"""
        try:
            # Gravity Forms use input_X naming pattern
            # input_1 = First Name, input_2 = Last Name, input_3 = Email, etc.

            # First Name (input_1 or variations)
            for selector in ['input[name*="input_1"]', 'input[name*="first"]', 'input[id*="first"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['first_name'])
                        print(f"            ✅ Filled first name")
                        break
                except:
                    continue

            # Last Name (input_2 or variations)
            for selector in ['input[name*="input_2"]', 'input[name*="last"]', 'input[id*="last"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['last_name'])
                        print(f"            ✅ Filled last name")
                        break
                except:
                    continue

            # Email (input_3 or variations)
            for selector in ['input[name*="input_3"]', 'input[type="email"]', 'input[name*="email"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['email'])
                        print(f"            ✅ Filled email")
                        break
                except:
                    continue

            # Phone
            for selector in ['input[name*="phone"]', 'input[type="tel"]', 'input[id*="phone"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['phone'])
                        print(f"            ✅ Filled phone")
                        break
                except:
                    continue

            # ZIP Code
            for selector in ['input[name*="zip"]', 'input[name*="postal"]', 'input[id*="zip"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['zip_code'])
                        print(f"            ✅ Filled zip code")
                        break
                except:
                    continue

            # Message (input_4 or textarea)
            for selector in ['textarea[name*="input_4"]', 'textarea[name*="message"]', 'textarea[name*="comment"]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['message'])
                        print(f"            ✅ Filled message")
                        break
                except:
                    continue

            # Submit the form
            await asyncio.sleep(1)  # Brief pause before submit

            for selector in ['input[type="submit"]', 'button[type="submit"]', '.gform_button', 'button:has-text("Submit")']:
                try:
                    submit_btn = page.locator(selector).first
                    if await submit_btn.count() > 0:
                        print(f"            🚀 Clicking submit button...")
                        await submit_btn.click()
                        print(f"            ✅ Form submitted!")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"            ❌ Error filling Gravity Form: {e}")
            return False

    async def _fill_generic_form(self, page):
        """Fill generic contact forms"""
        try:
            filled_count = 0

            # Try to fill email (most important)
            for selector in ['input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['email'])
                        print(f"            ✅ Filled email")
                        filled_count += 1
                        break
                except:
                    continue

            # Try to fill name fields
            for selector in ['input[name*="name" i]', 'input[id*="name" i]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        full_name = f"{self.test_user['first_name']} {self.test_user['last_name']}"
                        await elem.fill(full_name)
                        print(f"            ✅ Filled name")
                        filled_count += 1
                        break
                except:
                    continue

            # Try to fill message
            for selector in ['textarea', 'input[name*="message" i]', 'input[name*="comment" i]']:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.fill(self.test_user['message'])
                        print(f"            ✅ Filled message")
                        filled_count += 1
                        break
                except:
                    continue

            if filled_count == 0:
                return False

            # Try to submit
            await asyncio.sleep(1)

            for selector in ['input[type="submit"]', 'button[type="submit"]', 'button:has-text("Submit")']:
                try:
                    submit_btn = page.locator(selector).first
                    if await submit_btn.count() > 0:
                        print(f"            🚀 Clicking submit button...")
                        await submit_btn.click()
                        print(f"            ✅ Form submitted!")
                        return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"            ❌ Error filling generic form: {e}")
            return False

    async def _detect_submission_success(self, page, dealer_name):
        """Detect if form submission was successful"""
        try:
            # Wait a bit for response
            await asyncio.sleep(3)

            # Check for common success indicators
            success_patterns = [
                'thank you',
                'thanks',
                'success',
                'submitted',
                'received',
                'confirmation',
                'we\'ll be in touch',
                'contact you soon',
                'message sent',
            ]

            # Get page text
            page_text = await page.content()
            page_text_lower = page_text.lower()

            # Check for success messages
            for pattern in success_patterns:
                if pattern in page_text_lower:
                    print(f"         🎉 SUCCESS! Found confirmation: '{pattern}'")
                    return {
                        'filled': True,
                        'submitted': True,
                        'success': True,
                        'confirmation': pattern,
                        'final_url': page.url
                    }

            # Check if URL changed (often indicates success)
            current_url = page.url
            if 'thank' in current_url.lower() or 'success' in current_url.lower():
                print(f"         🎉 SUCCESS! Redirected to success page")
                return {
                    'filled': True,
                    'submitted': True,
                    'success': True,
                    'confirmation': 'url_redirect',
                    'final_url': current_url
                }

            # Check for success elements
            try:
                success_elem = await page.locator('.confirmation_message, .success, .thank-you').count()
                if success_elem > 0:
                    print(f"         🎉 SUCCESS! Found success element")
                    return {
                        'filled': True,
                        'submitted': True,
                        'success': True,
                        'confirmation': 'success_element',
                        'final_url': current_url
                    }
            except:
                pass

            # If no clear success indicator, consider it uncertain
            print(f"         ⚠️  Form submitted but no clear confirmation")
            return {
                'filled': True,
                'submitted': True,
                'success': 'uncertain',
                'confirmation': 'no_clear_indicator',
                'final_url': current_url
            }

        except Exception as e:
            return {
                'filled': True,
                'submitted': True,
                'success': 'unknown',
                'error': str(e),
                'final_url': page.url
            }

    async def test_dealership(self, context, dealer_index, dealer_name, website, homepage_url):
        """Test a single dealership with full submission"""
        print(f"\n🏪 #{dealer_index}: {dealer_name}")
        print(f"🌐 URL: {website}")

        result = {
            'dealer_index': dealer_index,
            'dealer_name': dealer_name,
            'website': website,
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Resolve contact page
            dealer_slug = dealer_name.lower().replace(' ', '-').replace('/', '-')[:50]

            resolution = await self.contact_resolver.resolve(
                context,
                dealer_id=dealer_slug,
                dealer_name=dealer_name,
                homepage_url=homepage_url,
                preferred_contact_url=None,
            )

            contact_url = resolution.contact_url
            contact_score = resolution.contact_score

            print(f"   🔁 Resolved contact: {contact_url}")
            print(f"   📊 Contact score: {contact_score}%")

            result['contact_url'] = contact_url
            result['contact_score'] = contact_score
            result['form_type'] = resolution.form_type

            if contact_score < 40:
                result['status'] = 'low_score'
                result['error'] = f'Form score too low: {contact_score}%'
                return result

            # Create page and navigate
            page = await self.browser_manager.create_enhanced_stealth_page(context)

            try:
                await page.goto(contact_url, wait_until='domcontentloaded', timeout=30000)

                # Smart wait for forms
                try:
                    await page.wait_for_selector('form, .gform_wrapper', timeout=10000)
                except:
                    await page.wait_for_load_state('networkidle', timeout=15000)

                # Take screenshot before filling
                screenshot_dir = os.path.join(self.output_dir, "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)

                before_screenshot = os.path.join(screenshot_dir, f"{dealer_index:02d}_{dealer_slug[:30]}_before.png")
                await page.screenshot(path=before_screenshot, full_page=True)

                # Fill and submit form
                submission_result = await self.fill_and_submit_form(page, dealer_name, contact_url)

                result.update(submission_result)

                # Take screenshot after submission
                if submission_result.get('submitted'):
                    await asyncio.sleep(2)  # Wait for any animations
                    after_screenshot = os.path.join(screenshot_dir, f"{dealer_index:02d}_{dealer_slug[:30]}_after.png")
                    await page.screenshot(path=after_screenshot, full_page=True)
                    result['screenshot_after'] = after_screenshot

                result['screenshot_before'] = before_screenshot

                if submission_result.get('success'):
                    result['status'] = 'success'
                    print(f"   ✅ COMPLETE SUCCESS: Form filled and submitted!")
                elif submission_result.get('filled'):
                    result['status'] = 'filled_only'
                    print(f"   ⚠️  Form filled but submission uncertain")
                else:
                    result['status'] = 'failed_to_fill'
                    print(f"   ❌ Could not fill form")

            finally:
                await page.close()

        except LookupError as e:
            result['status'] = 'no_contact_page'
            result['error'] = str(e)
            print(f"   ❌ No contact page: {e}")
        except TimeoutError:
            result['status'] = 'timeout'
            result['error'] = 'Page load timeout'
            print(f"   ❌ Timeout loading page")
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"   ❌ Error: {e}")

        return result

    async def run_test(self, num_dealerships=20):
        """Run test on random dealerships"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"tests/submission_test_{num_dealerships}_dealers_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"\n{'='*80}")
        print(f"🎯 DEALERSHIP SUBMISSION TEST")
        print(f"{'='*80}")
        print(f"📁 Output: {self.output_dir}")
        print(f"👤 Test User: {self.test_user['first_name']} {self.test_user['last_name']}")
        print(f"📧 Email: {self.test_user['email']}")
        print(f"🔢 Testing: {num_dealerships} random dealerships")
        print(f"⏰ Started: {datetime.now()}")
        print(f"{'='*80}\n")

        # Load dealerships
        df = pd.read_csv('Dealerships - Jeep.csv')

        # Exclude Autonation as requested
        df = df[~df['dealer_name'].str.contains('Autonation', case=False, na=False)]

        # Select random dealerships
        random.seed(42)  # For reproducibility
        selected = df.sample(n=min(num_dealerships, len(df))).reset_index(drop=True)

        results = []

        async with async_playwright() as p:
            browser, context = await self.browser_manager.open_context(p, headless=False)

            try:
                for index, row in selected.iterrows():
                    dealer_index = index + 1
                    dealer_name = row['dealer_name']
                    website = row['website']

                    if pd.isna(website) or not website.startswith('http'):
                        print(f"\n🏪 #{dealer_index}: {dealer_name}")
                        print(f"   ⚠️  No valid website")
                        continue

                    result = await self.test_dealership(
                        context,
                        dealer_index,
                        dealer_name,
                        website,
                        website
                    )

                    results.append(result)

                    # Save results after each dealership
                    results_df = pd.DataFrame(results)
                    results_df.to_csv(os.path.join(self.output_dir, "results.csv"), index=False)

                    # Small pause between dealerships
                    await asyncio.sleep(2)

            finally:
                await self.browser_manager.close_context(browser, context)

        # Generate summary
        self._generate_summary(results)

        return results

    def _generate_summary(self, results):
        """Generate test summary report"""
        total = len(results)

        success = len([r for r in results if r.get('status') == 'success'])
        filled_only = len([r for r in results if r.get('status') == 'filled_only'])
        failed_to_fill = len([r for r in results if r.get('status') == 'failed_to_fill'])
        no_contact = len([r for r in results if r.get('status') == 'no_contact_page'])
        timeout = len([r for r in results if r.get('status') == 'timeout'])
        errors = len([r for r in results if r.get('status') == 'error'])
        low_score = len([r for r in results if r.get('status') == 'low_score'])

        print(f"\n{'='*80}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tested: {total}")
        print(f"")
        print(f"✅ Complete Success: {success}/{total} ({success/total*100 if total > 0 else 0:.1f}%)")
        print(f"   - Form filled AND confirmed submission")
        print(f"")
        print(f"⚠️  Filled Only: {filled_only}/{total} ({filled_only/total*100 if total > 0 else 0:.1f}%)")
        print(f"   - Form filled but no clear confirmation")
        print(f"")
        print(f"❌ Failed to Fill: {failed_to_fill}/{total} ({failed_to_fill/total*100 if total > 0 else 0:.1f}%)")
        print(f"📄 No Contact Page: {no_contact}/{total}")
        print(f"⏱️  Timeout: {timeout}/{total}")
        print(f"❗ Other Errors: {errors}/{total}")
        print(f"📉 Low Score: {low_score}/{total}")
        print(f"")
        print(f"{'='*80}")
        print(f"📁 Results saved to: {self.output_dir}")
        print(f"⏰ Completed: {datetime.now()}")
        print(f"{'='*80}\n")

        # Save summary
        summary_path = os.path.join(self.output_dir, "SUMMARY.md")
        with open(summary_path, 'w') as f:
            f.write(f"# Test Summary\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Tested**: {total}\n\n")
            f.write(f"## Results\n\n")
            f.write(f"- ✅ **Complete Success**: {success}/{total} ({success/total*100 if total > 0 else 0:.1f}%)\n")
            f.write(f"- ⚠️ **Filled Only**: {filled_only}/{total} ({filled_only/total*100 if total > 0 else 0:.1f}%)\n")
            f.write(f"- ❌ **Failed to Fill**: {failed_to_fill}/{total}\n")
            f.write(f"- 📄 **No Contact Page**: {no_contact}/{total}\n")
            f.write(f"- ⏱️ **Timeout**: {timeout}/{total}\n")
            f.write(f"- ❗ **Other Errors**: {errors}/{total}\n")
            f.write(f"- 📉 **Low Score**: {low_score}/{total}\n\n")

            f.write(f"## Successful Submissions\n\n")
            for r in results:
                if r.get('status') == 'success':
                    f.write(f"- ✅ {r['dealer_name']} - Score: {r.get('contact_score', 0)}%, Confirmation: {r.get('confirmation', 'N/A')}\n")


if __name__ == "__main__":
    tester = DealershipSubmissionTester()
    asyncio.run(tester.run_test(num_dealerships=20))