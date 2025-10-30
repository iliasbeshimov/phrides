#!/usr/bin/env python3
"""
FINAL RETEST WITH CONTACT URLS - Using direct contact URLs like the working detector
Fix for the failed retest - use direct contact page URLs instead of homepage navigation
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
import re
from urllib.parse import urlparse

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from contact_page_detector import ContactPageDetector
from src.services.contact.contact_page_cache import (
    ContactPageResolver,
    ContactPageStore,
)

class FinalRetestWithContactUrls:
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

    async def detect_gravity_forms(self, page, dealer_name):
        """Simple Gravity Forms detection - same as working detector"""
        try:
            gform_count = await page.locator('.gform_wrapper').count()
            if gform_count > 0:
                print(f"      ✅ Found {gform_count} Gravity Forms")

                # Get form details
                form_info = await page.evaluate("""
                    () => {
                        const gforms = document.querySelectorAll('.gform_wrapper form');
                        return Array.from(gforms).map((form, i) => {
                            const inputs = Array.from(form.querySelectorAll('input, textarea, select'));

                            let score = 0;
                            let emailFields = 0;
                            let nameFields = 0;
                            let messageFields = 0;

                            inputs.forEach(inp => {
                                const label = inp.closest('li')?.querySelector('label')?.innerText?.toLowerCase() || '';
                                const name = inp.name || '';
                                const type = inp.type || '';

                                // Gravity Forms patterns
                                if (type === 'email' || label.includes('email') || name === 'input_3') {
                                    emailFields++;
                                    score += 30;
                                }
                                if (label.includes('first name') || name === 'input_1') {
                                    nameFields++;
                                    score += 20;
                                }
                                if (label.includes('last name') || name === 'input_2') {
                                    nameFields++;
                                    score += 15;
                                }
                                if (inp.tagName.toLowerCase() === 'textarea' || label.includes('message') || name === 'input_4') {
                                    messageFields++;
                                    score += 25;
                                }
                                if (label.includes('phone') || type === 'tel') {
                                    score += 10;
                                }
                                if (label.includes('zip')) {
                                    score += 5;
                                }
                            });

                            return {
                                formId: form.id,
                                formIndex: i,
                                totalInputs: inputs.filter(inp => inp.type !== 'hidden' && inp.type !== 'submit').length,
                                emailFields: emailFields,
                                nameFields: nameFields,
                                messageFields: messageFields,
                                contactScore: Math.min(score, 100),
                                formType: 'gravity_forms'
                            };
                        });
                    }
                """)

                # Display all forms found
                for form in form_info:
                    if form['contactScore'] > 0:
                        print(f"         📋 GForm {form['formIndex']+1}: {form['contactScore']}% score, {form['totalInputs']} inputs")
                        print(f"            {form['emailFields']} email, {form['nameFields']} name, {form['messageFields']} message")

                # Return the BEST form (highest score), not just the first
                if form_info:
                    best_form = max(form_info, key=lambda f: f.get('contactScore', 0))
                    if best_form['contactScore'] >= 40:  # Minimum threshold
                        print(f"         🎯 Best form: #{best_form['formIndex']+1} with {best_form['contactScore']}% score")
                        return best_form

        except Exception as e:
            print(f"      ❌ Gravity Forms detection error: {e}")

        return None

    async def test_failed_dealerships_with_contact_urls(self):
        """Test failed dealerships using direct contact URLs"""

        # Failed sites with DIRECT CONTACT URLs (like the working detector)
        failed_sites = [
            {
                'name': 'Thomas Garage Inc',
                'homepage_url': 'https://www.thomasautocenters.com/',
                'contact_url': 'https://www.thomasautocenters.com/contact-us/',
            },
            {
                'name': 'Autonation Chrysler Southwest',
                'homepage_url': 'https://www.autonationchryslerdodgejeepramsouthwest.com/',
                'contact_url': 'https://www.autonationchryslerdodgejeepramsouthwest.com/contact-us/',
            },
            {
                'name': 'Thomson Chrysler (Jeep Cheap)',
                'homepage_url': 'https://www.jeepcheap.com/',
                'contact_url': 'https://www.jeepcheap.com/contact-us/',
            },
            {
                'name': 'Tilleman Motor Co',
                'homepage_url': 'https://www.tillemanmotor.net/',
                'contact_url': 'https://www.tillemanmotor.net/contact-us/',
            },
            {
                'name': 'Rairdons Chrysler Kirkland',
                'homepage_url': 'https://www.dodgechryslerjeepofkirkland.com/',
                'contact_url': 'https://www.dodgechryslerjeepofkirkland.com/contact-us/',
            },
            {
                'name': 'Tasca Chrysler White Plains',
                'homepage_url': 'https://www.tascacdjrwhiteplains.com/',
                'contact_url': 'https://www.tascacdjrwhiteplains.com/contact-us/',
            },
            {
                'name': 'Downtown Auto Group',
                'homepage_url': 'https://www.buydowntown.com/',
                'contact_url': 'https://www.buydowntown.com/contact-us/',
            },
            {
                'name': 'Capital City Cdjr',
                'homepage_url': 'https://www.capcitycdjr.com/',
                'contact_url': 'https://www.CapCityCDJR.com/contact-us/',
            },
            {
                'name': 'Premier Chrysler Lamesa',
                'homepage_url': 'https://www.trucktowntexas.com/',
                'contact_url': 'https://www.trucktowntexas.com/contact-us/',
            },
            {
                'name': 'Shepherds Chrysler',
                'homepage_url': 'https://www.shepherdscdjr.com/',
                'contact_url': 'https://www.shepherdscdjr.com/contact-us/',
            },
            {
                'name': 'Steele Chrysler Lockhart',
                'homepage_url': 'https://www.steelechryslerlockhart.com/',
                'contact_url': 'https://www.steelechryslerlockhart.com/contactus.aspx',
            },
        ]

        # Setup output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"tests/final_retest_contact_urls_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)

        print(f"🎯 FINAL RETEST WITH DIRECT CONTACT URLS")
        print(f"📁 Output: {output_dir}")
        print(f"🔄 Testing {len(failed_sites)} failed dealerships with direct contact URLs")
        print(f"🚀 Using same method as working gravity_forms_detector.py")

        results = []
        successful_detections = 0

        async with async_playwright() as p:
            browser, context = await self.browser_manager.open_context(p)

            try:
                for i, site in enumerate(failed_sites):
                    dealer_index = i + 1
                    dealer_name = site['name']
                    contact_url = site['contact_url']

                    print(f"\n🏪 #{dealer_index}: {dealer_name}")
                    print(f"📞 Contact URL: {contact_url}")

                    slug = self._dealer_slug(dealer_name)
                    homepage_url = site.get('homepage_url') or self._homepage_from_contact(contact_url)

                    try:
                        resolution = await self.contact_resolver.resolve(
                            context,
                            dealer_id=slug,
                            dealer_name=dealer_name,
                            homepage_url=homepage_url,
                            preferred_contact_url=contact_url,
                        )
                        resolved_url = resolution.contact_url
                        print(
                            f"   🔁 Resolved contact page ({resolution.source}): {resolved_url}"
                        )
                    except LookupError as err:
                        print(f"   ❌ Contact page resolution failed: {err}")
                        results.append({
                            'dealer_name': dealer_name,
                            'contact_url': contact_url,
                            'homepage_url': homepage_url,
                            'original_status': 'failed',
                            'final_retest_status': 'still_failed',
                            'error': str(err),
                        })
                        continue

                    summary = (resolution.metadata or {}).get("best_form_summary")
                    if summary and summary.get('contactScore', 0) >= 40:
                        successful_detections += 1
                        print(
                            f"   🎯 SUCCESS (resolver): {summary['contactScore']}% score, {summary['totalInputs']} inputs"
                        )
                        result = {
                            'dealer_name': dealer_name,
                            'contact_url': resolved_url,
                            'contact_resolution_source': resolution.source,
                            'homepage_url': homepage_url,
                            'original_status': 'failed',
                            'final_retest_status': 'success',
                            'contact_score': summary['contactScore'],
                            'form_type': summary.get('formType', 'discovered'),
                            'total_inputs': summary['totalInputs'],
                            'email_fields': summary.get('emailFields', 0),
                            'name_fields': summary.get('nameFields', 0),
                            'message_fields': summary.get('messageFields', 0),
                            'screenshot_path': None,
                        }
                        results.append(result)
                        continue

                    page = await self.browser_manager.create_enhanced_stealth_page(context)

                    try:
                        await page.goto(resolved_url, wait_until='domcontentloaded', timeout=30000)

                        # Smart waiting: Wait for actual content
                        try:
                            await page.wait_for_selector('.gform_wrapper, form', timeout=10000)
                        except:
                            await page.wait_for_load_state('networkidle', timeout=15000)

                        # Detect Gravity Forms
                        detected_form = await self.detect_gravity_forms(page, dealer_name)

                        if detected_form:
                            successful_detections += 1
                            print(f"   🎯 SUCCESS: {detected_form['contactScore']}% score, {detected_form['totalInputs']} inputs")

                            # Take screenshot
                            screenshot_path = os.path.join(output_dir, "screenshots", f"{dealer_name.replace(' ', '_').replace('/', '-')}_success.png")
                            await page.screenshot(path=screenshot_path, full_page=True)

                            result = {
                                'dealer_name': dealer_name,
                                'contact_url': resolved_url,
                                'contact_resolution_source': resolution.source,
                                'homepage_url': homepage_url,
                                'original_status': 'failed',
                                'final_retest_status': 'success',
                                'contact_score': detected_form['contactScore'],
                                'form_type': detected_form['formType'],
                                'total_inputs': detected_form['totalInputs'],
                                'email_fields': detected_form['emailFields'],
                                'name_fields': detected_form['nameFields'],
                                'message_fields': detected_form['messageFields'],
                                'screenshot_path': screenshot_path
                            }
                        else:
                            print(f"   ❌ No Gravity Forms detected on contact page")
                            result = {
                                'dealer_name': dealer_name,
                                'contact_url': resolved_url,
                                'contact_resolution_source': resolution.source,
                                'homepage_url': homepage_url,
                                'original_status': 'failed',
                                'final_retest_status': 'still_failed'
                            }

                        results.append(result)

                    except Exception as e:
                        print(f"   ❌ Error accessing contact page: {e}")
                        results.append({
                            'dealer_name': dealer_name,
                            'contact_url': resolved_url,
                            'contact_resolution_source': resolution.source,
                            'homepage_url': homepage_url,
                            'original_status': 'failed',
                            'final_retest_status': 'error',
                            'error': str(e)
                        })
                    finally:
                        await page.close()

            finally:
                await self.browser_manager.close_context(browser, context)

        # Save results
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(output_dir, "final_retest_results.csv"), index=False)

        # Summary
        still_failed = len([r for r in results if r.get('final_retest_status') == 'still_failed'])
        errors = len([r for r in results if r.get('final_retest_status') == 'error'])

        print(f"\n🎯 FINAL RETEST COMPLETE!")
        print(f"✅ SUCCESS: {successful_detections}/{len(failed_sites)} ({successful_detections/len(failed_sites)*100:.1f}%)")
        print(f"❌ Still failed: {still_failed}/{len(failed_sites)}")
        print(f"⚠️ Errors: {errors}/{len(failed_sites)}")
        print(f"📈 IMPROVEMENT: {successful_detections} additional successful detections using direct contact URLs!")

        # Show which ones succeeded
        if successful_detections > 0:
            print(f"\n🎉 NEWLY SUCCESSFUL DEALERSHIPS:")
            for r in results:
                if r.get('final_retest_status') == 'success':
                    print(f"   ✅ {r['dealer_name']}: {r['contact_score']}% ({r['form_type']})")

        return results

    def _dealer_slug(self, dealer_name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", dealer_name.lower()).strip("-")
        return slug or "dealer"

    def _homepage_from_contact(self, contact_url: str) -> str:
        parsed = urlparse(contact_url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/"
        return contact_url

if __name__ == "__main__":
    detector = FinalRetestWithContactUrls()
    asyncio.run(detector.test_failed_dealerships_with_contact_urls())
