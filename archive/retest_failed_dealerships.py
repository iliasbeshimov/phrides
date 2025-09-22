#!/usr/bin/env python3
"""
RETEST FAILED DEALERSHIPS - Using improved Gravity Forms detection
Test all 11 dealerships that failed in the original 40-dealership test
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

class ImprovedContactDetector:
    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()

    async def detect_contact_forms_improved(self, page, dealer_name):
        """Improved detection with Gravity Forms support"""
        print(f"   🔍 Improved contact form detection for {dealer_name}")
        
        all_forms = []
        
        # Wait for dynamic content
        await page.wait_for_timeout(10000)
        
        try:
            # 1. Standard Gravity Forms detection
            gforms = await self.detect_gravity_forms(page)
            all_forms.extend(gforms)
            
            # 2. Standard form detection (for non-Gravity forms)
            standard_forms = await self.detect_standard_forms(page)
            all_forms.extend(standard_forms)
            
            # 3. Navigate to contact page if not already there
            current_url = page.url
            if '/contact' not in current_url.lower():
                contact_forms = await self.try_contact_page_navigation(page, dealer_name)
                all_forms.extend(contact_forms)
                
        except Exception as e:
            print(f"      ❌ Detection error: {e}")
            
        return all_forms

    async def detect_gravity_forms(self, page):
        """Detect Gravity Forms specifically"""
        gravity_forms = []
        
        try:
            gform_count = await page.locator('.gform_wrapper').count()
            if gform_count > 0:
                print(f"      ✅ Found {gform_count} Gravity Forms")
                
                gform_analysis = await page.evaluate("""
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
                
                for form in gform_analysis:
                    if form['contactScore'] > 0:
                        print(f"         📋 GForm {form['formIndex']+1}: {form['contactScore']}% score, {form['totalInputs']} inputs")
                        print(f"            {form['emailFields']} email, {form['nameFields']} name, {form['messageFields']} message")
                        gravity_forms.append(form)
                        
        except Exception as e:
            print(f"      ❌ Gravity Forms detection error: {e}")
            
        return gravity_forms

    async def detect_standard_forms(self, page):
        """Detect standard HTML forms (non-Gravity)"""
        standard_forms = []
        
        try:
            form_analysis = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form:not(.gform_wrapper form)');
                    return Array.from(forms).map((form, i) => {
                        const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                        
                        let score = 0;
                        let emailFields = 0;
                        let nameFields = 0;
                        let messageFields = 0;
                        
                        inputs.forEach(inp => {
                            const name = (inp.name || '').toLowerCase();
                            const id = (inp.id || '').toLowerCase();
                            const placeholder = (inp.placeholder || '').toLowerCase();
                            const type = inp.type || '';
                            const combined = name + ' ' + id + ' ' + placeholder;
                            
                            if (type === 'email' || combined.includes('email')) {
                                emailFields++;
                                score += 30;
                            }
                            if (combined.includes('name') || combined.includes('first') || combined.includes('last')) {
                                nameFields++;
                                score += 15;
                            }
                            if (inp.tagName.toLowerCase() === 'textarea' || combined.includes('message') || combined.includes('comment')) {
                                messageFields++;
                                score += 25;
                            }
                            if (type === 'tel' || combined.includes('phone')) {
                                score += 10;
                            }
                        });
                        
                        return {
                            formIndex: i,
                            totalInputs: inputs.filter(inp => inp.type !== 'hidden' && inp.type !== 'submit').length,
                            emailFields: emailFields,
                            nameFields: nameFields,
                            messageFields: messageFields,
                            contactScore: Math.min(score, 100),
                            formType: 'standard'
                        };
                    });
                }
            """)
            
            for form in form_analysis:
                if form['contactScore'] >= 50:
                    print(f"         📋 Standard Form {form['formIndex']+1}: {form['contactScore']}% score, {form['totalInputs']} inputs")
                    standard_forms.append(form)
                    
        except Exception as e:
            print(f"      ❌ Standard forms detection error: {e}")
            
        return standard_forms

    async def try_contact_page_navigation(self, page, dealer_name):
        """Try to navigate to contact page if not already there"""
        contact_forms = []
        
        try:
            # Look for contact links
            contact_patterns = [
                'a:has-text("Contact Us")',
                'a:has-text("Contact")',
                'a[href*="contact"]'
            ]
            
            for pattern in contact_patterns:
                try:
                    links = await page.locator(pattern).all()
                    if links:
                        # Try first contact link
                        href = await links[0].get_attribute('href')
                        if href and '/contact' in href.lower():
                            print(f"      🔗 Navigating to contact page: {href}")
                            await links[0].click()
                            await page.wait_for_timeout(5000)
                            
                            # Detect forms on contact page
                            contact_gforms = await self.detect_gravity_forms(page)
                            contact_standard = await self.detect_standard_forms(page)
                            contact_forms.extend(contact_gforms)
                            contact_forms.extend(contact_standard)
                            break
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"      ❌ Contact navigation error: {e}")
            
        return contact_forms

    async def test_failed_dealerships(self):
        """Test all dealerships that failed in the original 40-dealership test"""
        
        # All failed dealerships from original test
        failed_sites = [
            {'name': 'Thomas Garage Inc', 'url': 'https://www.thomasautocenters.com'},
            {'name': 'Autonation Chrysler Dodge Jeep Ram Southwest', 'url': 'https://www.autonationchryslerdodgejeepramsouthwest.com'},
            {'name': 'Thomson Chrysler Dodge Jeep Ram FIAT', 'url': 'https://www.jeepcheap.com'},
            {'name': 'Tilleman Motor Co.', 'url': 'https://www.tillemanmotor.net'},
            {'name': 'Rairdon\'s Chrysler Jeep Dodge of Kirkland', 'url': 'https://www.dodgechryslerjeepofkirkland.com'},
            {'name': 'Tasca Chrysler Dodge Jeep Ram White Plains', 'url': 'https://www.tascacdjrwhiteplains.com'},
            {'name': 'Downtown Auto Group Inc', 'url': 'https://www.buydowntown.com'},
            {'name': 'Capital City Cdjr', 'url': 'https://www.CapCityCDJR.com'},
            {'name': 'Premier Chrysler Dodge Jeep Ram of Lamesa', 'url': 'https://www.trucktowntexas.com'},
            {'name': 'Shepherd\'s Chrysler Dodge Jeep Ram', 'url': 'https://www.shepherdscdjr.com'},
            {'name': 'Steele Chrysler Jeep Dodge Ram Lockhart', 'url': 'https://www.steelechryslerlockhart.com'}
        ]

        # Setup output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"tests/retest_failed_dealerships_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)

        print(f"🎯 RETEST FAILED DEALERSHIPS")
        print(f"📁 Output: {output_dir}")
        print(f"🔄 Retesting {len(failed_sites)} previously failed dealerships")
        print(f"🚀 Using improved Gravity Forms + standard detection")

        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            for i, site in enumerate(failed_sites):
                dealer_index = i + 1
                dealer_name = site['name']
                website = site['url']

                print(f"\n🏪 #{dealer_index}: {dealer_name}")
                print(f"🌐 URL: {website}")

                context = await self.browser_manager.create_enhanced_stealth_context(browser)
                page = await context.new_page()

                try:
                    # Navigate
                    await page.goto(website, wait_until='domcontentloaded', timeout=45000)

                    # Improved detection
                    detected_forms = await self.detect_contact_forms_improved(page, dealer_name)

                    if detected_forms:
                        best_form = max(detected_forms, key=lambda x: x['contactScore'])

                        print(f"   🎯 BEST FORM: {best_form['contactScore']}% score ({best_form['formType']})")
                        print(f"   📊 Total forms: {len(detected_forms)}")
                        print(f"   📋 Best form: {best_form['totalInputs']} inputs, {best_form['emailFields']} email, {best_form['nameFields']} name, {best_form['messageFields']} message")

                        # Take screenshot
                        screenshot_path = os.path.join(output_dir, "screenshots", f"{dealer_name.replace(' ', '_').replace('/', '-')}_retest.png")
                        await page.screenshot(path=screenshot_path, full_page=True)

                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'original_status': 'failed',
                            'retest_status': 'success',
                            'contact_score': best_form['contactScore'],
                            'form_type': best_form['formType'],
                            'total_inputs': best_form['totalInputs'],
                            'email_fields': best_form['emailFields'],
                            'name_fields': best_form['nameFields'],
                            'message_fields': best_form['messageFields'],
                            'screenshot_path': screenshot_path
                        }
                    else:
                        print(f"   ❌ Still no contact forms detected")
                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'original_status': 'failed',
                            'retest_status': 'still_failed'
                        }

                    results.append(result)

                except Exception as e:
                    print(f"   ❌ Retest error: {e}")
                    results.append({
                        'dealer_name': dealer_name,
                        'website': website,
                        'original_status': 'failed',
                        'retest_status': 'error',
                        'error': str(e)
                    })
                finally:
                    await context.close()

            await browser.close()

        # Save results
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(output_dir, "retest_results.csv"), index=False)

        # Summary
        successful_retests = len([r for r in results if r.get('retest_status') == 'success'])
        still_failed = len([r for r in results if r.get('retest_status') == 'still_failed'])
        errors = len([r for r in results if r.get('retest_status') == 'error'])

        print(f"\n🎯 RETEST COMPLETE!")
        print(f"✅ Now successful: {successful_retests}/{len(failed_sites)} ({successful_retests/len(failed_sites)*100:.1f}%)")
        print(f"❌ Still failed: {still_failed}/{len(failed_sites)}")
        print(f"⚠️ Errors: {errors}/{len(failed_sites)}")
        print(f"📈 IMPROVEMENT: {successful_retests} additional successful detections!")
        
        # Show which ones succeeded
        if successful_retests > 0:
            print(f"\n🎉 NEWLY SUCCESSFUL DEALERSHIPS:")
            for r in results:
                if r.get('retest_status') == 'success':
                    print(f"   ✅ {r['dealer_name']}: {r['contact_score']}% ({r['form_type']})")

        return results

if __name__ == "__main__":
    detector = ImprovedContactDetector()
    asyncio.run(detector.test_failed_dealerships())
