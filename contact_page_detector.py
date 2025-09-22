#!/usr/bin/env python3
"""
CONTACT PAGE DETECTOR - Navigate to Contact Pages and Find Sales Forms
Goal: Find contact page links, navigate to them, and detect sales contact forms
Focus on actual contact forms rather than inventory search forms
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
import numpy as np

class ContactPageDetector:
    """Advanced detector that finds contact pages and their forms"""

    def __init__(self):
        # Contact page link patterns
        self.contact_link_patterns = [
            'a:has-text("Contact")',
            'a:has-text("Contact Us")',
            'a:has-text("Get Quote")',
            'a:has-text("Request Quote")',
            'a:has-text("Sales")',
            'a:has-text("Service")',
            'a:has-text("Get Price")',
            'a:has-text("Inquiry")',
            'a[href*="contact"]',
            'a[href*="quote"]',
            'a[href*="sales"]',
            'a[href*="inquiry"]',
            'a[href*="lead"]',
            '.contact-link',
            '.quote-link'
        ]

        # Sales-specific form indicators (high priority)
        self.sales_indicators = [
            'sales', 'contact', 'inquiry', 'quote', 'price', 'inventory',
            'vehicle', 'car', 'auto', 'financing', 'lease', 'buy', 'purchase'
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
            '.inquiry-form',
            '.quote-form'
        ]

        # Input patterns that suggest contact forms
        self.contact_input_patterns = [
            'input[type="email"]',
            'input[name*="email" i]',
            'input[name*="name" i]',
            'input[name*="phone" i]',
            'input[name*="first" i]',
            'input[name*="last" i]',
            'textarea[name*="message" i]',
            'textarea[name*="comment" i]',
            'select[name*="interest" i]',
            'select[name*="model" i]'
        ]

    async def find_contact_links(self, page):
        """Find all potential contact page links"""
        print(f"      🔍 Searching for contact page links...")

        contact_links = []

        for pattern in self.contact_link_patterns:
            try:
                links = await page.locator(pattern).all()
                for link in links:
                    try:
                        text = await link.inner_text()
                        href = await link.get_attribute('href')

                        if href and text:
                            # Clean up the link
                            text = text.strip().lower()

                            # Filter for relevant contact links
                            if any(keyword in text for keyword in ['contact', 'quote', 'sales', 'inquiry', 'service']):
                                contact_links.append({
                                    'text': text,
                                    'href': href,
                                    'pattern': pattern
                                })
                                print(f"         ✅ Found: '{text}' -> {href}")
                    except Exception:
                        continue
            except Exception:
                continue

        # Remove duplicates based on href
        unique_links = []
        seen_hrefs = set()
        for link in contact_links:
            if link['href'] not in seen_hrefs:
                seen_hrefs.add(link['href'])
                unique_links.append(link)

        print(f"      📊 Found {len(unique_links)} unique contact links")
        return unique_links

    def calculate_sales_relevance_score(self, form_text, form_attributes, page_url=""):
        """Calculate how likely this form is for sales contact"""
        score = 0
        text_content = (form_text or '').lower()
        attrs_content = (form_attributes or '').lower()
        url_content = (page_url or '').lower()
        combined_content = f"{text_content} {attrs_content} {url_content}"

        # High-value sales indicators
        high_value_terms = ['sales', 'quote', 'price', 'inventory', 'financing', 'lease', 'purchase']
        for term in high_value_terms:
            if term in combined_content:
                score += 20

        # Medium-value contact indicators
        medium_value_terms = ['contact', 'inquiry', 'vehicle', 'car', 'auto', 'dealership']
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

        # Boost for being on contact pages
        if any(term in url_content for term in ['contact', 'quote', 'sales', 'inquiry']):
            score += 20

        return min(score, 100)  # Cap at 100%

    async def detect_forms_on_page(self, page, page_name, page_url):
        """Detect and classify all forms on the current page"""
        print(f"         📋 Scanning forms on: {page_name}")

        detected_forms = []

        try:
            # Wait for page to load
            await page.wait_for_timeout(10000)  # 10 seconds

            # Find all forms using different patterns
            all_forms = []
            for pattern in self.form_patterns:
                try:
                    forms = await page.locator(pattern).all()
                    if forms:
                        print(f"            ✅ Found {len(forms)} forms with pattern: {pattern}")
                        all_forms.extend(forms)
                except Exception:
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

            print(f"            📊 Total unique forms: {len(unique_forms)}")

            # Analyze each form
            for i, form in enumerate(unique_forms):
                try:
                    # Get form text content
                    form_text = await form.inner_text() if await form.is_visible() else ""

                    # Get form attributes
                    form_attributes = f"{await form.get_attribute('id') or ''} {await form.get_attribute('class') or ''} {await form.get_attribute('name') or ''}"

                    # Count inputs by type
                    input_count = 0
                    email_inputs = 0
                    name_inputs = 0
                    phone_inputs = 0
                    textareas = 0

                    for input_pattern in self.contact_input_patterns:
                        try:
                            inputs = await form.locator(input_pattern).all()
                            count = len(inputs)
                            input_count += count

                            if 'email' in input_pattern:
                                email_inputs += count
                            elif 'name' in input_pattern:
                                name_inputs += count
                            elif 'phone' in input_pattern:
                                phone_inputs += count
                            elif 'textarea' in input_pattern:
                                textareas += count
                        except Exception:
                            continue

                    # Calculate sales relevance score
                    relevance_score = self.calculate_sales_relevance_score(form_text, form_attributes, page_url)

                    # Get form position for screenshot
                    bbox = await form.bounding_box()

                    form_info = {
                        'form_index': i + 1,
                        'page_name': page_name,
                        'page_url': page_url,
                        'relevance_score': relevance_score,
                        'total_inputs': input_count,
                        'email_inputs': email_inputs,
                        'name_inputs': name_inputs,
                        'phone_inputs': phone_inputs,
                        'textareas': textareas,
                        'form_text_preview': form_text[:200] if form_text else "",
                        'form_attributes': form_attributes,
                        'bbox': bbox,
                        'is_visible': await form.is_visible()
                    }

                    detected_forms.append(form_info)

                    print(f"               Form #{i+1}: {relevance_score}% score, {input_count} total inputs")
                    print(f"                          {email_inputs} email, {name_inputs} name, {phone_inputs} phone, {textareas} textarea")

                except Exception as e:
                    print(f"               ⚠️ Error analyzing form #{i+1}: {e}")
                    continue

            return detected_forms

        except Exception as e:
            print(f"            ❌ Error during form detection: {e}")
            return []

    async def take_form_screenshot(self, page, form_info, dealer_name, output_dir):
        """Take a screenshot of the detected form"""
        try:
            page_name = form_info['page_name']
            form_index = form_info['form_index']
            relevance_score = form_info['relevance_score']

            # Create filename
            safe_dealer = dealer_name.replace(' ', '_').replace('/', '-').replace('&', 'and')[:15]
            safe_page = page_name.replace(' ', '_').replace('/', '-')[:10]
            filename = f"{safe_dealer}_{safe_page}_form{form_index}_score{relevance_score:.0f}.png"
            screenshot_path = os.path.join(output_dir, "screenshots", filename)

            # Take screenshot
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"               📸 Screenshot: {filename}")

            return screenshot_path

        except Exception as e:
            print(f"               ❌ Screenshot error: {e}")
            return None

class ContactPageDetectionTest:
    def __init__(self):
        self.results = []
        self.detector = ContactPageDetector()
        self.browser_manager = EnhancedStealthBrowserManager()

    async def test_single_dealer(self, browser, dealer_index, dealer_name, website):
        """Test contact page detection on a single dealership website"""

        print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
        print(f"🌐 URL: {website}")

        context = await self.browser_manager.create_enhanced_stealth_context(browser)
        page = await context.new_page()

        all_detected_forms = []
        best_form = None

        try:
            # Navigate to main page
            print(f"   🚀 Navigating to homepage...")
            await page.goto(website, wait_until='domcontentloaded', timeout=30000)

            # Check for forms on homepage first
            homepage_forms = await self.detector.detect_forms_on_page(page, "Homepage", website)
            all_detected_forms.extend(homepage_forms)

            # Find contact page links
            contact_links = await self.detector.find_contact_links(page)

            # Visit each contact page
            for link_info in contact_links[:3]:  # Limit to top 3 links to save time
                try:
                    href = link_info['href']
                    link_text = link_info['text']

                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        base_url = website.rstrip('/')
                        full_url = f"{base_url}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue

                    print(f"      🔗 Visiting: {link_text} ({full_url})")

                    # Navigate to contact page
                    await page.goto(full_url, wait_until='domcontentloaded', timeout=20000)

                    # Detect forms on this page
                    contact_forms = await self.detector.detect_forms_on_page(page, link_text.title(), full_url)
                    all_detected_forms.extend(contact_forms)

                except Exception as e:
                    print(f"      ❌ Error visiting {link_info['text']}: {e}")
                    continue

            # Find the best form overall
            if all_detected_forms:
                # Sort by relevance score
                all_detected_forms.sort(key=lambda x: x['relevance_score'], reverse=True)
                best_form = all_detected_forms[0]

                # Take screenshot of best form
                if best_form['relevance_score'] > 30:  # Only screenshot promising forms
                    # Navigate back to the page with the best form
                    if best_form['page_url'] != page.url:
                        await page.goto(best_form['page_url'], wait_until='domcontentloaded', timeout=20000)
                        await asyncio.sleep(3)

                    screenshot_path = await self.detector.take_form_screenshot(
                        page, best_form, dealer_name, self.output_dir
                    )
                    best_form['screenshot_path'] = screenshot_path

            # Prepare result
            result = {
                'dealer_index': dealer_index,
                'dealer_name': dealer_name,
                'website': website,
                'status': 'no_forms_found',
                'contact_links_found': len(contact_links),
                'total_forms_detected': len(all_detected_forms),
                'best_form_score': 0,
                'best_form_page': '',
                'timestamp': datetime.now().isoformat()
            }

            if best_form:
                result.update({
                    'status': 'forms_detected',
                    'best_form_score': best_form['relevance_score'],
                    'best_form_page': best_form['page_name'],
                    'best_form_inputs': best_form['total_inputs'],
                    'best_form_emails': best_form['email_inputs'],
                    'screenshot_path': best_form.get('screenshot_path', '')
                })

                print(f"   🎯 BEST FORM: {best_form['relevance_score']}% score on '{best_form['page_name']}' page")
                print(f"   📊 SUMMARY: {len(contact_links)} contact links, {len(all_detected_forms)} total forms")
            else:
                print(f"   ❌ No suitable forms found ({len(contact_links)} links checked)")

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

    async def run_contact_detection_test(self, test_count=10):
        """Run contact page detection test on sample dealerships"""

        # Setup output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"tests/contact_page_detection_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)

        print(f"🎯 CONTACT PAGE DETECTION TEST")
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
                    results_df.to_csv(os.path.join(self.output_dir, f"contact_detection_results.csv"), index=False)

                    # Short pause between dealers
                    await asyncio.sleep(2)
                else:
                    print(f"\n🏪 #{dealer_index:02d}: {dealer_name}")
                    print(f"   ⚠️ No valid website")

            await browser.close()

        # Final summary
        forms_found = len([r for r in self.results if r['status'] == 'forms_detected'])
        high_score_forms = len([r for r in self.results if r.get('best_form_score', 0) > 50])
        total_contact_links = sum([r.get('contact_links_found', 0) for r in self.results])

        print(f"\n🎯 CONTACT DETECTION COMPLETE!")
        print(f"📊 Dealerships with forms: {forms_found}/{len(self.results)}")
        print(f"🎖️ High-quality forms (>50% score): {high_score_forms}")
        print(f"🔗 Total contact links found: {total_contact_links}")
        print(f"⏰ Completed: {datetime.now()}")

if __name__ == "__main__":
    # Test with 40 dealerships for broader analysis
    tester = ContactPageDetectionTest()
    asyncio.run(tester.run_contact_detection_test(40))