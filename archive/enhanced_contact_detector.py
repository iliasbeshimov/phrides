#!/usr/bin/env python3
"""
ENHANCED CONTACT DETECTOR - Advanced form detection for modern websites
Addresses the 5 major failure patterns identified in investigation:
1. Dynamic content loading
2. Modal/popup forms
3. Hidden/invisible elements
4. Modern JavaScript frameworks
5. Third-party form services
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
import numpy as np

class EnhancedContactDetector:
    """Advanced detector that handles modern website challenges"""

    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()

        # Enhanced form patterns including modern frameworks
        self.form_patterns = [
            'form', '.gform_wrapper', 'form[id*="gform_"]',
            'form[name*="contact"]', 'form[name*="sales"]',
            '.wpforms-form', '.contact-form', '.lead-form',
            '.inquiry-form', '.quote-form',
            # React/Vue/Angular patterns
            '[data-form]', '[data-contact-form]', '[role="form"]',
            '.react-form', '.vue-form', '.ng-form'
        ]

        # Enhanced input patterns for modern forms
        self.input_patterns = [
            'input[type="email"]', 'input[name*="email" i]',
            'input[name*="name" i]', 'input[name*="phone" i]',
            'input[name*="first" i]', 'input[name*="last" i]',
            'textarea[name*="message" i]', 'textarea[name*="comment" i]',
            'select[name*="interest" i]', 'select[name*="model" i]',
            # Modern form field patterns
            'input[data-field*="email"]', 'input[data-field*="name"]',
            'input[placeholder*="email" i]', 'input[placeholder*="name" i]'
        ]

        # Modal trigger patterns
        self.modal_patterns = [
            'a[href*="#modal"]', 'a[href*="#contact"]', 'a[href*="#quote"]',
            'button[data-toggle="modal"]', 'button[data-target*="modal"]',
            '.modal-trigger', '.contact-modal-trigger', '.quote-modal-trigger',
            'a[onclick*="modal"]', 'button[onclick*="modal"]'
        ]

    async def wait_for_dynamic_content(self, page, max_wait=30):
        """Enhanced waiting for dynamic content with multiple checks"""
        print(f"      ⏳ Waiting for dynamic content (up to {max_wait}s)...")

        initial_form_count = await page.evaluate("() => document.querySelectorAll('form').length")
        initial_input_count = await page.evaluate("() => document.querySelectorAll('input, textarea, select').length")

        print(f"         📊 Initial: {initial_form_count} forms, {initial_input_count} inputs")

        # Progressive waiting with checks every 5 seconds
        for wait_cycle in range(1, (max_wait // 5) + 1):
            await page.wait_for_timeout(5000)

            current_form_count = await page.evaluate("() => document.querySelectorAll('form').length")
            current_input_count = await page.evaluate("() => document.querySelectorAll('input, textarea, select').length")

            print(f"         📊 After {wait_cycle * 5}s: {current_form_count} forms, {current_input_count} inputs")

            # If content stabilized for 2 consecutive checks, we can proceed
            if wait_cycle > 1 and current_form_count == prev_form_count and current_input_count == prev_input_count:
                print(f"         ✅ Content stabilized after {wait_cycle * 5}s")
                break

            prev_form_count = current_form_count
            prev_input_count = current_input_count

        # Final scroll and wait to trigger any lazy loading
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(3000)

        final_form_count = await page.evaluate("() => document.querySelectorAll('form').length")
        final_input_count = await page.evaluate("() => document.querySelectorAll('input, textarea, select').length")

        if final_form_count > initial_form_count or final_input_count > initial_input_count:
            print(f"         🎯 Dynamic loading detected: +{final_form_count - initial_form_count} forms, +{final_input_count - initial_input_count} inputs")

    async def detect_and_trigger_modals(self, page):
        """Detect and trigger modal forms"""
        print(f"      🪟 Detecting and triggering modals...")

        modal_forms_found = []

        for pattern in self.modal_patterns:
            try:
                triggers = await page.locator(pattern).all()

                for i, trigger in enumerate(triggers):
                    try:
                        # Check if trigger is contact-related
                        trigger_text = await trigger.inner_text() if await trigger.is_visible() else ""
                        trigger_href = await trigger.get_attribute('href') or ""

                        if any(keyword in (trigger_text + trigger_href).lower()
                               for keyword in ['contact', 'quote', 'inquiry', 'sales']):

                            print(f"         🎯 Found modal trigger: '{trigger_text.strip()}'")

                            # Try to trigger the modal
                            await trigger.click()
                            await page.wait_for_timeout(2000)  # Wait for modal to appear

                            # Look for forms in modals
                            modal_forms = await self.detect_forms_in_modals(page)
                            modal_forms_found.extend(modal_forms)

                            # Close modal (try common methods)
                            await self.close_modal(page)

                    except Exception as e:
                        print(f"         ⚠️ Error triggering modal {i}: {e}")
                        continue

            except Exception:
                continue

        return modal_forms_found

    async def detect_forms_in_modals(self, page):
        """Detect forms specifically within modal dialogs"""
        modal_selectors = [
            '.modal form', '.popup form', '.dialog form',
            '.overlay form', '.lightbox form', '[role="dialog"] form',
            '.modal-content form', '.modal-body form'
        ]

        modal_forms = []

        for selector in modal_selectors:
            try:
                forms = await page.locator(selector).all()
                for form in forms:
                    if await form.is_visible():
                        form_info = await self.analyze_single_form(form, page, "Modal")
                        if form_info:
                            modal_forms.append(form_info)
                            print(f"         ✅ Modal form found: {form_info['relevance_score']}% score")
            except Exception:
                continue

        return modal_forms

    async def close_modal(self, page):
        """Try to close modal dialogs using common methods"""
        close_selectors = [
            '.modal .close', '.popup .close', '.dialog .close',
            '[aria-label="Close"]', '[title="Close"]', '.modal-close',
            'button:has-text("Close")', 'button:has-text("×")',
            '.overlay', '.modal-backdrop'
        ]

        for selector in close_selectors:
            try:
                close_button = page.locator(selector).first
                if await close_button.is_visible():
                    await close_button.click()
                    await page.wait_for_timeout(1000)
                    break
            except Exception:
                continue

    async def detect_hidden_forms(self, page):
        """Detect forms that might be hidden but become visible"""
        print(f"      👁️ Detecting hidden forms...")

        hidden_forms = []

        # Look for forms that are hidden but might become visible
        hidden_form_js = """
            () => {
                const hiddenForms = [];
                document.querySelectorAll('form').forEach((form, index) => {
                    const style = window.getComputedStyle(form);
                    const isHidden = style.display === 'none' ||
                                   style.visibility === 'hidden' ||
                                   style.opacity === '0' ||
                                   form.offsetParent === null;

                    if (isHidden) {
                        hiddenForms.push({
                            index: index,
                            id: form.id,
                            className: form.className,
                            innerHTML: form.innerHTML.substring(0, 200)
                        });
                    }
                });
                return hiddenForms;
            }
        """

        hidden_form_info = await page.evaluate(hidden_form_js)

        if hidden_form_info:
            print(f"         🔍 Found {len(hidden_form_info)} hidden forms")

            # Try to make hidden forms visible
            for form_info in hidden_form_info:
                try:
                    # Try different methods to show the form
                    show_methods = [
                        f"document.querySelectorAll('form')[{form_info['index']}].style.display = 'block'",
                        f"document.querySelectorAll('form')[{form_info['index']}].style.visibility = 'visible'",
                        f"document.querySelectorAll('form')[{form_info['index']}].style.opacity = '1'"
                    ]

                    for method in show_methods:
                        await page.evaluate(method)

                    await page.wait_for_timeout(1000)

                    # Check if form is now visible and analyze it
                    form_locator = page.locator('form').nth(form_info['index'])
                    if await form_locator.is_visible():
                        form_analysis = await self.analyze_single_form(form_locator, page, "Hidden->Visible")
                        if form_analysis:
                            hidden_forms.append(form_analysis)
                            print(f"         ✅ Hidden form revealed: {form_analysis['relevance_score']}% score")

                except Exception as e:
                    print(f"         ⚠️ Error revealing hidden form: {e}")
                    continue

        return hidden_forms

    async def analyze_single_form(self, form_locator, page, page_context):
        """Analyze a single form element with enhanced patterns"""
        try:
            # Get form text and attributes
            form_text = await form_locator.inner_text() if await form_locator.is_visible() else ""
            form_html = await form_locator.inner_html()
            form_id = await form_locator.get_attribute('id') or ""
            form_class = await form_locator.get_attribute('class') or ""
            form_name = await form_locator.get_attribute('name') or ""

            # Enhanced input counting with modern patterns
            input_counts = {
                'total_inputs': 0,
                'email_inputs': 0,
                'name_inputs': 0,
                'phone_inputs': 0,
                'textareas': 0
            }

            for pattern in self.input_patterns:
                try:
                    inputs = await form_locator.locator(pattern).all()
                    count = len(inputs)
                    input_counts['total_inputs'] += count

                    if 'email' in pattern.lower():
                        input_counts['email_inputs'] += count
                    elif 'name' in pattern.lower():
                        input_counts['name_inputs'] += count
                    elif 'phone' in pattern.lower():
                        input_counts['phone_inputs'] += count
                    elif 'textarea' in pattern.lower():
                        input_counts['textareas'] += count

                except Exception:
                    continue

            # Enhanced relevance scoring
            relevance_score = self.calculate_enhanced_relevance_score(
                form_text, f"{form_id} {form_class} {form_name}",
                page_context, input_counts
            )

            return {
                'page_context': page_context,
                'relevance_score': relevance_score,
                'form_text_preview': form_text[:200],
                'form_attributes': f"{form_id} {form_class} {form_name}",
                **input_counts
            }

        except Exception as e:
            print(f"         ❌ Error analyzing form: {e}")
            return None

    def calculate_enhanced_relevance_score(self, form_text, form_attributes, page_context, input_counts):
        """Enhanced scoring algorithm with modern considerations"""
        score = 0
        text_content = (form_text or '').lower()
        attrs_content = (form_attributes or '').lower()
        context_content = (page_context or '').lower()
        combined_content = f"{text_content} {attrs_content} {context_content}"

        # High-value sales indicators (increased weight)
        high_value_terms = ['sales', 'quote', 'price', 'inventory', 'financing', 'lease', 'purchase']
        for term in high_value_terms:
            if term in combined_content:
                score += 25  # Increased from 20

        # Medium-value contact indicators
        medium_value_terms = ['contact', 'inquiry', 'vehicle', 'car', 'auto', 'dealership', 'get started']
        for term in medium_value_terms:
            if term in combined_content:
                score += 15  # Increased from 10

        # Enhanced input scoring
        if input_counts['email_inputs'] > 0:
            score += 20  # Increased importance
        if input_counts['name_inputs'] > 0:
            score += 15
        if input_counts['phone_inputs'] > 0:
            score += 15
        if input_counts['textareas'] > 0:
            score += 10

        # Bonus for good form structure
        if input_counts['total_inputs'] >= 5:
            score += 10
        if input_counts['total_inputs'] >= 8:
            score += 10  # Extra bonus for comprehensive forms

        # Context bonuses
        if 'contact' in context_content:
            score += 20
        if 'modal' in context_content:
            score += 15  # Modal forms are often high-quality
        if 'hidden' in context_content:
            score += 10  # Successfully revealed hidden forms

        return min(score, 100)

    async def comprehensive_form_detection(self, page, dealer_name, page_url):
        """Comprehensive form detection using all advanced techniques"""
        print(f"   🔍 Comprehensive form detection for {dealer_name}")

        all_detected_forms = []

        # Step 1: Wait for dynamic content
        await self.wait_for_dynamic_content(page)

        # Step 2: Standard form detection
        print(f"      📋 Standard form detection...")
        for pattern in self.form_patterns:
            try:
                forms = await page.locator(pattern).all()
                for form in forms:
                    if await form.is_visible():
                        form_analysis = await self.analyze_single_form(form, page, "Standard")
                        if form_analysis:
                            all_detected_forms.append(form_analysis)
            except Exception:
                continue

        # Step 3: Modal detection and triggering
        modal_forms = await self.detect_and_trigger_modals(page)
        all_detected_forms.extend(modal_forms)

        # Step 4: Hidden form detection
        hidden_forms = await self.detect_hidden_forms(page)
        all_detected_forms.extend(hidden_forms)

        # Step 5: iframe form detection
        iframe_forms = await self.detect_iframe_forms(page)
        all_detected_forms.extend(iframe_forms)

        return all_detected_forms

    async def detect_iframe_forms(self, page):
        """Detect forms within iframes"""
        print(f"      🖼️ Detecting iframe forms...")

        iframe_forms = []

        try:
            iframes = await page.locator('iframe').all()

            for i, iframe in enumerate(iframes):
                try:
                    src = await iframe.get_attribute('src') or ""

                    # Check if iframe might contain forms
                    if any(keyword in src.lower() for keyword in ['form', 'contact', 'quote', 'lead']):
                        print(f"         🎯 Potential form iframe: {src}")

                        # Try to access iframe content (if same-origin)
                        try:
                            iframe_content = await iframe.content_frame()
                            if iframe_content:
                                iframe_form_count = await iframe_content.evaluate("() => document.querySelectorAll('form').length")
                                if iframe_form_count > 0:
                                    print(f"         ✅ Found {iframe_form_count} forms in iframe")
                                    iframe_forms.append({
                                        'page_context': f"iframe-{i}",
                                        'relevance_score': 75,  # Assume good quality if in form-related iframe
                                        'form_text_preview': f"Iframe form: {src}",
                                        'total_inputs': iframe_form_count,
                                        'iframe_src': src
                                    })
                        except Exception:
                            # Cross-origin iframe, can't access content
                            pass

                except Exception:
                    continue

        except Exception:
            pass

        return iframe_forms

# Main test class with enhanced detection
class EnhancedContactTest:
    def __init__(self):
        self.detector = EnhancedContactDetector()
        self.results = []

    async def test_failed_sites(self):
        """Test the enhanced detector on previously failed sites"""

        failed_sites = [
            {'name': 'Autonation Chrysler', 'url': 'https://www.autonationchryslerdodgejeepramsouthwest.com'},
            {'name': 'Capital City Cdjr', 'url': 'https://www.CapCityCDJR.com'},
            {'name': 'Thomas Garage Inc', 'url': 'https://www.thomasautocenters.com'},
            {'name': 'Rairdon\'s Chrysler', 'url': 'https://www.dodgechryslerjeepofkirkland.com'},
            {'name': 'Jerry Ulm Chrysler', 'url': 'https://www.jerryulmchryslerdodgejeepram.com'}
        ]

        # Setup output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"tests/enhanced_detection_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)

        print(f"🚀 ENHANCED DETECTION TEST")
        print(f"📁 Output: {output_dir}")
        print(f"🎯 Testing {len(failed_sites)} previously failed sites")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for i, site in enumerate(failed_sites):
                dealer_index = i + 1
                dealer_name = site['name']
                website = site['url']

                print(f"\n🏪 #{dealer_index}: {dealer_name}")
                print(f"🌐 URL: {website}")

                context = await self.detector.browser_manager.create_enhanced_stealth_context(browser)
                page = await context.new_page()

                try:
                    # Navigate
                    await page.goto(website, wait_until='domcontentloaded', timeout=45000)

                    # Enhanced detection
                    detected_forms = await self.detector.comprehensive_form_detection(page, dealer_name, website)

                    # Find best form
                    if detected_forms:
                        best_form = max(detected_forms, key=lambda x: x['relevance_score'])

                        print(f"   🎯 BEST FORM: {best_form['relevance_score']}% score ({best_form['page_context']})")
                        print(f"   📊 Total forms found: {len(detected_forms)}")

                        # Take screenshot
                        screenshot_path = os.path.join(output_dir, "screenshots", f"{dealer_name.replace(' ', '_')}_enhanced.png")
                        await page.screenshot(path=screenshot_path, full_page=True)

                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'status': 'enhanced_success',
                            'forms_detected': len(detected_forms),
                            'best_form_score': best_form['relevance_score'],
                            'best_form_context': best_form['page_context'],
                            'best_form_inputs': best_form.get('total_inputs', 0),
                            'screenshot_path': screenshot_path
                        }
                    else:
                        print(f"   ❌ Still no forms detected with enhanced methods")
                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'status': 'enhanced_failed',
                            'forms_detected': 0
                        }

                    self.results.append(result)

                except Exception as e:
                    print(f"   ❌ Enhanced test error: {e}")
                    self.results.append({
                        'dealer_name': dealer_name,
                        'website': website,
                        'status': 'error',
                        'error': str(e)
                    })
                finally:
                    await context.close()

            await browser.close()

        # Save results
        results_df = pd.DataFrame(self.results)
        results_df.to_csv(os.path.join(output_dir, "enhanced_detection_results.csv"), index=False)

        # Summary
        successful = len([r for r in self.results if r.get('status') == 'enhanced_success'])
        print(f"\n🎯 ENHANCED DETECTION COMPLETE!")
        print(f"✅ Success rate: {successful}/{len(failed_sites)} ({successful/len(failed_sites)*100:.1f}%)")
        print(f"📈 Improvement: Previously 0/5 failed sites, now {successful}/5 detected")

if __name__ == "__main__":
    tester = EnhancedContactTest()
    asyncio.run(tester.test_failed_sites())