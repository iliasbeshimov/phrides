#!/usr/bin/env python3
"""
RESUME 50 DEALERSHIP TEST - Continue from where we left off
Continue testing remaining dealerships from the interrupted complete_50_test.py
Based on screenshots, we completed through dealership #19, need to continue from #20+
"""

import asyncio
import random
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
import numpy as np

class EfficientDetector:
    """Efficient detector optimized for speed while maintaining accuracy"""

    def __init__(self):
        # Most effective form patterns (reduced set for speed)
        self.form_patterns = [
            'form', '.gform_wrapper', 'form[id*="gform_"]',
            'form[name*="contact"]', '.wpforms-form'
        ]

        # Key input patterns
        self.input_patterns = [
            'input[type="email"]', 'input[name*="email" i]',
            'input[name*="name" i]', 'textarea'
        ]

        # Submit patterns
        self.submit_patterns = [
            'button[type="submit"]', 'input[type="submit"]', '.gform_button'
        ]

    async def quick_detection(self, page, max_wait_seconds=20):
        """Quick 20-second detection optimized for speed"""

        print("   ⚡ Quick detection (20-second max wait)...")

        result = {
            'success': False,
            'confidence_score': 0.0,
            'forms_found': 0,
            'inputs_found': 0,
            'buttons_found': 0,
            'framework': 'Standard HTML'
        }

        try:
            # 2-cycle quick scan (20 seconds total)
            for cycle in range(2):
                await page.wait_for_timeout(10000)  # 10 seconds per cycle
                print(f"         Quick cycle {cycle + 1}/2...")

                # Form detection
                total_forms = 0
                for pattern in self.form_patterns:
                    try:
                        forms = await page.locator(pattern).all()
                        if len(forms) > 0:
                            total_forms += len(forms)
                            print(f"            ✅ {len(forms)} forms: {pattern}")
                            break  # Early exit on first match
                    except Exception:
                        continue

                # Input detection (quick check)
                total_inputs = 0
                for pattern in self.input_patterns:
                    try:
                        inputs = await page.locator(pattern).all()
                        total_inputs += len(inputs)
                    except Exception:
                        continue

                result['forms_found'] = max(result['forms_found'], total_forms)
                result['inputs_found'] = max(result['inputs_found'], total_inputs)

                print(f"            📊 Quick cycle {cycle + 1}: {total_forms} forms, {total_inputs} inputs")

                # Early success detection
                if total_forms > 0 or total_inputs >= 2:
                    print(f"            🎉 Forms detected in cycle {cycle + 1}!")
                    break

            # Quick JavaScript check
            js_result = await page.evaluate("""
                () => ({
                    allForms: document.querySelectorAll('form').length,
                    emailInputs: document.querySelectorAll('input[type="email"], input[name*="email"]').length,
                    hasGravityForms: document.querySelectorAll('.gform_wrapper').length > 0
                })
            """)

            # Quick confidence calculation
            confidence = 0.0
            if result['forms_found'] > 0 or js_result['allForms'] > 0:
                confidence += 40
            if result['inputs_found'] >= 2:
                confidence += 30
            if js_result['emailInputs'] > 0:
                confidence += 30

            result['confidence_score'] = confidence
            result['success'] = confidence >= 60

            print(f"         🎯 Quick detection result: {confidence:.1f}% confidence")
            return result

        except Exception as e:
            print(f"         ❌ Quick detection error: {e}")
            return result

    async def attempt_form_submission(self, page, dealer_name):
        """Attempt to fill and submit contact form"""
        print(f"   📝 Attempting form submission for {dealer_name}...")

        try:
            # Look for email input first
            email_input = None
            email_patterns = [
                'input[type="email"]',
                'input[name*="email" i]',
                'input[id*="email" i]'
            ]

            for pattern in email_patterns:
                try:
                    email_locator = page.locator(pattern).first
                    if await email_locator.is_visible():
                        email_input = email_locator
                        print(f"      ✅ Found email input: {pattern}")
                        break
                except Exception:
                    continue

            if not email_input:
                print(f"      ❌ No email input found")
                return False

            # Fill email
            await email_input.fill("test@example.com")
            print(f"      📧 Email filled")

            # Look for name field
            name_patterns = [
                'input[name*="name" i]',
                'input[id*="name" i]',
                'input[placeholder*="name" i]'
            ]

            for pattern in name_patterns:
                try:
                    name_locator = page.locator(pattern).first
                    if await name_locator.is_visible():
                        await name_locator.fill("John Smith")
                        print(f"      👤 Name filled: {pattern}")
                        break
                except Exception:
                    continue

            # Look for message/comment field
            message_patterns = [
                'textarea',
                'input[name*="message" i]',
                'input[name*="comment" i]'
            ]

            for pattern in message_patterns:
                try:
                    message_locator = page.locator(pattern).first
                    if await message_locator.is_visible():
                        await message_locator.fill("Hi, I'm interested in learning more about your vehicles and services. Please contact me. Thanks!")
                        print(f"      💬 Message filled: {pattern}")
                        break
                except Exception:
                    continue

            # Wait a moment for any JavaScript validation
            await page.wait_for_timeout(2000)

            # Look for submit button
            submit_patterns = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.gform_button',
                'button:has-text("Submit")',
                'button:has-text("Send")',
                'input[value*="Submit" i]'
            ]

            for pattern in submit_patterns:
                try:
                    submit_locator = page.locator(pattern).first
                    if await submit_locator.is_visible():
                        print(f"      🚀 Submitting via: {pattern}")
                        await submit_locator.click()

                        # Wait for submission response
                        await page.wait_for_timeout(3000)

                        # Check for success indicators
                        success_indicators = [
                            'text=thank you',
                            'text=success',
                            'text=submitted',
                            'text=received',
                            '.success',
                            '.thank-you'
                        ]

                        for indicator in success_indicators:
                            try:
                                if await page.locator(indicator).count() > 0:
                                    print(f"      🎉 SUCCESS! Found: {indicator}")
                                    return True
                            except Exception:
                                continue

                        print(f"      ✅ Form submitted (no explicit success message)")
                        return True

                except Exception as e:
                    print(f"      ⚠️ Submit attempt failed for {pattern}: {e}")
                    continue

            print(f"      ❌ No submit button found")
            return False

        except Exception as e:
            print(f"      ❌ Form submission error: {e}")
            return False

class ResumeDealer50Test:
    def __init__(self):
        self.results = []
        self.detector = EfficientDetector()
        self.browser_manager = EnhancedStealthBrowserManager()

        # Track completed dealerships from previous run
        self.completed_dealers = {
            1: "Sahara_Motors_Inc",
            3: "Jones_Chrysler_Dodge",
            14: "Fletcher_Chrysler-Do",
            15: "Southfork_Chrysler_D",
            16: "Tubbs_Brothers_Inc",
            18: "Brownfield_Chrysler_",
            19: "Goldstein_Chrysler_J",
            20: "Griffin_Chrysler_Dod",
            23: "Savage_L&B_Dodge_Chr",
            25: "Heritage_Chrysler_Do",
            26: "Lampe_Chrysler_Dodge",
            27: "Ig_Burton_Chrysler_D",
            34: "Martin_Chrysler_LLC",
            37: "Vaughn_Chrysler_Jeep",
            40: "Bluebonnet_Motors_In",
            42: "Brad_Deery_Motors_In",
            46: "Fillback_Chrysler_Do",
            47: "Kayser_Chry_Center_o"
        }

    def get_screenshot_path(self, dealer_index, dealer_name, status=""):
        """Generate screenshot path"""
        safe_name = dealer_name.replace(' ', '_').replace('/', '-').replace('&', 'and')[:20]
        filename = f"{dealer_index:02d}_{safe_name}_{status}.png"
        return os.path.join(self.output_dir, "screenshots", filename)

    async def test_single_dealer(self, browser, dealer_index, dealer_name, website):
        """Test a single dealership with efficient approach"""

        print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
        print(f"🌐 URL: {website}")

        # Skip if already completed
        if dealer_index in self.completed_dealers:
            print(f"   ⏭️ Already completed in previous run")
            return {
                'dealer_index': dealer_index,
                'dealer_name': dealer_name,
                'website': website,
                'status': 'already_completed',
                'confidence_score': 100.0,
                'timestamp': datetime.now().isoformat()
            }

        context = await self.browser_manager.create_enhanced_stealth_context(browser)
        page = await context.new_page()

        try:
            # Navigate with timeout
            print(f"   🚀 Navigating...")
            await page.goto(website, wait_until='domcontentloaded', timeout=30000)

            # Quick detection (20 seconds max)
            detection_result = await self.detector.quick_detection(page)

            result = {
                'dealer_index': dealer_index,
                'dealer_name': dealer_name,
                'website': website,
                'status': 'failed',
                'confidence_score': detection_result['confidence_score'],
                'forms_found': detection_result['forms_found'],
                'inputs_found': detection_result['inputs_found'],
                'timestamp': datetime.now().isoformat()
            }

            if detection_result['success']:
                # Attempt form submission
                submission_success = await self.detector.attempt_form_submission(page, dealer_name)

                if submission_success:
                    result['status'] = 'success'
                    screenshot_path = self.get_screenshot_path(dealer_index, dealer_name, "success")
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"   📸 Success screenshot: {screenshot_path}")
                else:
                    result['status'] = 'form_submission_failed'
                    screenshot_path = self.get_screenshot_path(dealer_index, dealer_name, "failed")
                    await page.screenshot(path=screenshot_path, full_page=True)
            else:
                result['status'] = 'no_forms_detected'
                print(f"   ❌ No forms detected (confidence: {detection_result['confidence_score']:.1f}%)")

            return result

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'dealer_index': dealer_index,
                'dealer_name': dealer_name,
                'website': website,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            await context.close()

    async def run_remaining_dealers(self):
        """Resume testing from where we left off"""

        # Setup output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"tests/resume_50_dealers_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)

        print(f"🎯 RESUME 50 DEALERSHIP TEST")
        print(f"📁 Output: {self.output_dir}")
        print(f"⏰ Started: {datetime.now()}")

        # Load dealership data
        df = pd.read_csv('Dealerships - Jeep.csv')

        # Select 50 random dealerships (same seed for consistency)
        np.random.seed(42)
        selected_dealers = df.sample(n=50, random_state=42).reset_index(drop=True)

        print(f"📊 Total dealerships: {len(selected_dealers)}")
        print(f"✅ Already completed: {len(self.completed_dealers)}")
        print(f"🔄 Remaining to test: {50 - len(self.completed_dealers)}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for index, row in selected_dealers.iterrows():
                dealer_index = index + 1
                dealer_name = row['dealer_name']
                website = row['website']

                if not pd.isna(website) and website.startswith('http'):
                    result = await self.test_single_dealer(browser, dealer_index, dealer_name, website)
                    self.results.append(result)

                    # Save results after each dealer
                    results_df = pd.DataFrame(self.results)
                    results_df.to_csv(os.path.join(self.output_dir, f"resume_50_results.csv"), index=False)

                    # Short pause between dealers
                    await asyncio.sleep(2)
                else:
                    print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
                    print(f"   ⚠️ No valid website")

            await browser.close()

        # Final summary
        print(f"\n🎯 RESUME TEST COMPLETE!")
        print(f"📊 Total new attempts: {len([r for r in self.results if r['status'] != 'already_completed'])}")
        print(f"✅ New successes: {len([r for r in self.results if r['status'] == 'success'])}")
        print(f"❌ New failures: {len([r for r in self.results if r['status'] in ['failed', 'no_forms_detected', 'form_submission_failed', 'error']])}")
        print(f"⏰ Completed: {datetime.now()}")

if __name__ == "__main__":
    tester = ResumeDealer50Test()
    asyncio.run(tester.run_remaining_dealers())