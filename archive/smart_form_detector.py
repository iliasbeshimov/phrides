#!/usr/bin/env python3
"""
SMART FORM DETECTOR - Focus on Sales Contact Form Detection
Goal: Identify and screenshot sales contact forms on dealership websites
No form filling - just detection, classification, and screenshot capture
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
import numpy as np

class SalesFormDetector:
    """Advanced detector focused on identifying sales contact forms"""

    def __init__(self):
        # Sales-specific form indicators (high priority)
        self.sales_indicators = [
            'sales', 'contact', 'inquiry', 'quote', 'price', 'inventory',
            'vehicle', 'car', 'auto', 'financing', 'lease', 'buy'
        ]

        # Form patterns to search for
        self.form_patterns = [
            'form',
            '.gform_wrapper',
            'form[id*="gform_"]',
            'form[name*="contact"]',
            'form[name*="sales"]',
            '.wpforms-form',
            '.contact-form',
            '.lead-form',
            '.inquiry-form'
        ]

        # Input patterns that suggest contact forms
        self.contact_input_patterns = [
            'input[type="email"]',
            'input[name*="email" i]',
            'input[name*="name" i]',
            'input[name*="phone" i]',
            'textarea[name*="message" i]',
            'textarea[name*="comment" i]',
            'select[name*="interest" i]'
        ]

    def calculate_sales_relevance_score(self, form_text, form_attributes):
        """Calculate how likely this form is for sales contact"""
        score = 0
        text_content = (form_text or '').lower()
        attrs_content = (form_attributes or '').lower()
        combined_content = f"{text_content} {attrs_content}"

        # High-value sales indicators
        high_value_terms = ['sales', 'quote', 'price', 'inventory', 'financing', 'lease']
        for term in high_value_terms:
            if term in combined_content:
                score += 20

        # Medium-value contact indicators
        medium_value_terms = ['contact', 'inquiry', 'vehicle', 'car', 'auto']
        for term in medium_value_terms:
            if term in combined_content:
                score += 10

        # Form structure indicators
        if 'email' in combined_content:
            score += 15
        if 'name' in combined_content:
            score += 10
        if 'phone' in combined_content:
            score += 10
        if 'message' in combined_content or 'comment' in combined_content:
            score += 10

        return min(score, 100)  # Cap at 100%

    async def detect_forms_on_page(self, page, dealer_name):
        """Detect and classify all forms on the page"""
        print(f"   🔍 Scanning for forms on {dealer_name}...")

        detected_forms = []

        try:
            # Wait for page to load
            await page.wait_for_timeout(15000)  # 15 seconds for dynamic content

            # Find all forms using different patterns
            all_forms = []
            for pattern in self.form_patterns:
                try:
                    forms = await page.locator(pattern).all()
                    if forms:
                        print(f"      ✅ Found {len(forms)} forms with pattern: {pattern}")
                        all_forms.extend(forms)
                except Exception as e:
                    continue

            # Remove duplicates by tracking form positions
            unique_forms = []
            seen_positions = set()

            for form in all_forms:
                try:
                    bbox = await form.bounding_box()
                    if bbox:
                        position = (int(bbox['x']), int(bbox['y']))
                        if position not in seen_positions:
                            seen_positions.add(position)
                            unique_forms.append(form)
                except Exception:
                    continue

            print(f"      📊 Total unique forms found: {len(unique_forms)}")

            # Analyze each form
            for i, form in enumerate(unique_forms):
                try:
                    # Get form text content
                    form_text = await form.inner_text() if await form.is_visible() else ""

                    # Get form attributes
                    form_html = await form.inner_html()
                    form_attributes = f"{await form.get_attribute('id') or ''} {await form.get_attribute('class') or ''} {await form.get_attribute('name') or ''}"

                    # Count inputs
                    input_count = 0
                    email_inputs = 0
                    for input_pattern in self.contact_input_patterns:
                        try:
                            inputs = await form.locator(input_pattern).all()
                            input_count += len(inputs)
                            if 'email' in input_pattern:
                                email_inputs += len(inputs)
                        except Exception:
                            continue

                    # Calculate sales relevance score
                    relevance_score = self.calculate_sales_relevance_score(form_text, form_attributes)

                    # Get form position for screenshot
                    bbox = await form.bounding_box()

                    form_info = {
                        'form_index': i + 1,
                        'relevance_score': relevance_score,
                        'input_count': input_count,
                        'email_inputs': email_inputs,
                        'form_text_preview': form_text[:200] if form_text else "",
                        'form_attributes': form_attributes,
                        'bbox': bbox,
                        'is_visible': await form.is_visible()
                    }

                    detected_forms.append(form_info)

                    print(f"         Form #{i+1}: {relevance_score}% relevant, {input_count} inputs, {email_inputs} email fields")
                    if form_text:
                        preview = form_text.replace('\n', ' ')[:100]
                        print(f"                  Preview: {preview}...")

                except Exception as e:
                    print(f"         ⚠️ Error analyzing form #{i+1}: {e}")
                    continue

            # Sort forms by relevance score
            detected_forms.sort(key=lambda x: x['relevance_score'], reverse=True)

            return detected_forms

        except Exception as e:
            print(f"      ❌ Error during form detection: {e}")
            return []

    async def take_form_screenshot(self, page, form_info, dealer_name, output_dir):
        """Take a screenshot highlighting the detected form"""
        try:
            form_index = form_info['form_index']
            relevance_score = form_info['relevance_score']

            # Create filename
            safe_name = dealer_name.replace(' ', '_').replace('/', '-').replace('&', 'and')[:20]
            filename = f"{safe_name}_form{form_index}_score{relevance_score:.0f}.png"
            screenshot_path = os.path.join(output_dir, "screenshots", filename)

            # Take full page screenshot
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"         📸 Screenshot saved: {filename}")

            return screenshot_path

        except Exception as e:
            print(f"         ❌ Screenshot error: {e}")
            return None

class SmartFormDetectionTest:
    def __init__(self):
        self.results = []
        self.detector = SalesFormDetector()
        self.browser_manager = EnhancedStealthBrowserManager()

    async def test_single_dealer(self, browser, dealer_index, dealer_name, website):
        """Test form detection on a single dealership website"""

        print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
        print(f"🌐 URL: {website}")

        context = await self.browser_manager.create_enhanced_stealth_context(browser)
        page = await context.new_page()

        try:
            # Navigate with timeout
            print(f"   🚀 Navigating...")
            await page.goto(website, wait_until='domcontentloaded', timeout=30000)

            # Detect forms
            detected_forms = await self.detector.detect_forms_on_page(page, dealer_name)

            result = {
                'dealer_index': dealer_index,
                'dealer_name': dealer_name,
                'website': website,
                'status': 'no_forms_found',
                'forms_detected': len(detected_forms),
                'best_form_score': 0,
                'timestamp': datetime.now().isoformat(),
                'screenshot_path': None
            }

            if detected_forms:
                best_form = detected_forms[0]  # Highest scoring form
                result['status'] = 'forms_detected'
                result['best_form_score'] = best_form['relevance_score']
                result['best_form_inputs'] = best_form['input_count']
                result['best_form_emails'] = best_form['email_inputs']

                # Take screenshot of the best form
                screenshot_path = await self.detector.take_form_screenshot(
                    page, best_form, dealer_name, self.output_dir
                )
                result['screenshot_path'] = screenshot_path

                print(f"   🎯 BEST FORM: Score {best_form['relevance_score']}%, {best_form['input_count']} inputs")

                # Show all forms summary
                print(f"   📋 ALL FORMS SUMMARY:")
                for form in detected_forms:
                    print(f"      Form #{form['form_index']}: {form['relevance_score']}% score, {form['input_count']} inputs")
            else:
                print(f"   ❌ No forms detected")

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

    async def run_smart_detection_test(self, test_count=20):
        """Run smart form detection test on sample dealerships"""

        # Setup output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"tests/smart_form_detection_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)

        print(f"🎯 SMART FORM DETECTION TEST")
        print(f"📁 Output: {self.output_dir}")
        print(f"⏰ Started: {datetime.now()}")
        print(f"🎲 Testing {test_count} random dealerships")

        # Load dealership data
        df = pd.read_csv('Dealerships - Jeep.csv')

        # Select random dealerships
        np.random.seed(42)  # For reproducible results
        selected_dealers = df.sample(n=test_count, random_state=42).reset_index(drop=True)

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
                    results_df.to_csv(os.path.join(self.output_dir, f"smart_detection_results.csv"), index=False)

                    # Short pause between dealers
                    await asyncio.sleep(3)
                else:
                    print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
                    print(f"   ⚠️ No valid website")

            await browser.close()

        # Final summary
        forms_found = len([r for r in self.results if r['status'] == 'forms_detected'])
        total_forms = sum([r.get('forms_detected', 0) for r in self.results])

        print(f"\n🎯 SMART DETECTION COMPLETE!")
        print(f"📊 Dealerships with forms: {forms_found}/{len(self.results)}")
        print(f"📋 Total forms detected: {total_forms}")
        print(f"📸 Screenshots captured: {forms_found}")
        print(f"⏰ Completed: {datetime.now()}")

if __name__ == "__main__":
    # Test with 20 dealerships first
    tester = SmartFormDetectionTest()
    asyncio.run(tester.run_smart_detection_test(20))