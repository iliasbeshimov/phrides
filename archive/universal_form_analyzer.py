#!/usr/bin/env python3
"""
UNIVERSAL FORM ANALYZER - Dynamic form content analysis
Final solution: Instead of pattern matching, analyze actual form content
to identify contact forms regardless of naming conventions
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

class UniversalFormAnalyzer:
    """Analyzes actual form content without relying on naming patterns"""

    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()

    async def analyze_all_forms_on_page(self, page, dealer_name):
        """Analyze every form on the page regardless of naming conventions"""
        print(f"   🔬 Universal form analysis for {dealer_name}")

        # Wait for dynamic content
        await page.wait_for_timeout(15000)

        # Get all forms with comprehensive analysis
        form_analysis = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                const results = [];

                forms.forEach((form, index) => {
                    try {
                        // Get all inputs/textareas/selects within this form
                        const allInputs = Array.from(form.querySelectorAll('input, textarea, select'));

                        const analysis = {
                            formIndex: index,
                            formId: form.id || '',
                            formClass: form.className || '',
                            formName: form.name || '',
                            formAction: form.action || '',
                            formMethod: form.method || '',
                            isVisible: form.offsetParent !== null,
                            formText: form.innerText ? form.innerText.substring(0, 500) : '',

                            // Input analysis
                            totalInputs: allInputs.length,
                            inputDetails: [],

                            // Content analysis
                            hasEmailKeywords: false,
                            hasContactKeywords: false,
                            hasSalesKeywords: false,
                            hasNameKeywords: false,
                            hasPhoneKeywords: false,
                            hasMessageKeywords: false
                        };

                        // Analyze each input in detail
                        allInputs.forEach((input, inputIndex) => {
                            const inputDetail = {
                                index: inputIndex,
                                tag: input.tagName.toLowerCase(),
                                type: input.type || '',
                                name: input.name || '',
                                id: input.id || '',
                                className: input.className || '',
                                placeholder: input.placeholder || '',
                                value: input.value || '',
                                required: input.required || false,
                                visible: input.offsetParent !== null
                            };

                            // Analyze input content for purpose
                            const inputContent = `${inputDetail.name} ${inputDetail.id} ${inputDetail.className} ${inputDetail.placeholder}`.toLowerCase();

                            inputDetail.likelyPurpose = 'unknown';
                            if (inputContent.includes('email') || inputDetail.type === 'email') {
                                inputDetail.likelyPurpose = 'email';
                                analysis.hasEmailKeywords = true;
                            } else if (inputContent.includes('name') || inputContent.includes('first') || inputContent.includes('last')) {
                                inputDetail.likelyPurpose = 'name';
                                analysis.hasNameKeywords = true;
                            } else if (inputContent.includes('phone') || inputContent.includes('tel') || inputDetail.type === 'tel') {
                                inputDetail.likelyPurpose = 'phone';
                                analysis.hasPhoneKeywords = true;
                            } else if (input.tagName.toLowerCase() === 'textarea' || inputContent.includes('message') || inputContent.includes('comment')) {
                                inputDetail.likelyPurpose = 'message';
                                analysis.hasMessageKeywords = true;
                            }

                            analysis.inputDetails.push(inputDetail);
                        });

                        // Analyze form text content
                        const formTextLower = analysis.formText.toLowerCase();
                        analysis.hasContactKeywords = formTextLower.includes('contact') || formTextLower.includes('get in touch') || formTextLower.includes('reach out');
                        analysis.hasSalesKeywords = formTextLower.includes('sales') || formTextLower.includes('quote') || formTextLower.includes('price') || formTextLower.includes('buy');

                        // Calculate contact form likelihood
                        let likelihood = 0;

                        // Email field is crucial for contact forms
                        if (analysis.hasEmailKeywords) likelihood += 30;

                        // Name field is very common
                        if (analysis.hasNameKeywords) likelihood += 20;

                        // Message/comment field indicates contact intent
                        if (analysis.hasMessageKeywords) likelihood += 25;

                        // Phone field is good indicator
                        if (analysis.hasPhoneKeywords) likelihood += 15;

                        // Context keywords
                        if (analysis.hasContactKeywords) likelihood += 15;
                        if (analysis.hasSalesKeywords) likelihood += 20;

                        // Form structure bonus
                        if (analysis.totalInputs >= 3) likelihood += 10;
                        if (analysis.totalInputs >= 5) likelihood += 10;

                        // Visibility bonus
                        if (analysis.isVisible) likelihood += 5;

                        analysis.contactLikelihood = Math.min(likelihood, 100);

                        results.push(analysis);
                    } catch (error) {
                        console.log(`Error analyzing form ${index}:`, error);
                    }
                });

                return results;
            }
        """)

        print(f"      📊 Found {len(form_analysis)} forms to analyze")

        # Process and display results
        contact_forms = []
        for form in form_analysis:
            if form['contactLikelihood'] > 0:
                print(f"         📝 Form #{form['formIndex']}: {form['contactLikelihood']}% contact likelihood")
                print(f"            📋 {form['totalInputs']} inputs, visible: {form['isVisible']}")

                # Show input purposes
                purposes = {}
                for input_detail in form['inputDetails']:
                    purpose = input_detail['likelyPurpose']
                    purposes[purpose] = purposes.get(purpose, 0) + 1

                purpose_summary = ", ".join([f"{count} {purpose}" for purpose, count in purposes.items() if purpose != 'unknown'])
                if purpose_summary:
                    print(f"            🎯 Inputs: {purpose_summary}")

                if form['contactLikelihood'] >= 50:
                    contact_forms.append(form)

        return contact_forms

    async def test_universal_analysis(self):
        """Test universal analysis on failed sites"""

        failed_sites = [
            {'name': 'Autonation Chrysler', 'url': 'https://www.autonationchryslerdodgejeepramsouthwest.com'},
            {'name': 'Capital City Cdjr', 'url': 'https://www.CapCityCDJR.com'},
            {'name': 'Thomas Garage Inc', 'url': 'https://www.thomasautocenters.com'},
            {'name': 'Rairdon\'s Chrysler', 'url': 'https://www.dodgechryslerjeepofkirkland.com'},
            {'name': 'Jerry Ulm Chrysler', 'url': 'https://www.jerryulmchryslerdodgejeepram.com'}
        ]

        # Setup output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"tests/universal_analysis_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "screenshots"), exist_ok=True)

        print(f"🔬 UNIVERSAL FORM ANALYSIS TEST")
        print(f"📁 Output: {output_dir}")
        print(f"🎯 Testing {len(failed_sites)} previously failed sites")

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

                    # Universal analysis
                    contact_forms = await self.analyze_all_forms_on_page(page, dealer_name)

                    if contact_forms:
                        best_form = max(contact_forms, key=lambda x: x['contactLikelihood'])

                        print(f"   🎯 BEST CONTACT FORM: {best_form['contactLikelihood']}% likelihood")
                        print(f"   📊 {len(contact_forms)} potential contact forms found")

                        # Take screenshot
                        screenshot_path = os.path.join(output_dir, "screenshots", f"{dealer_name.replace(' ', '_')}_universal.png")
                        await page.screenshot(path=screenshot_path, full_page=True)

                        # Try to navigate to contact page for comparison
                        try:
                            contact_links = await page.locator('a:has-text("Contact")').all()
                            if contact_links:
                                await contact_links[0].click()
                                await page.wait_for_timeout(5000)

                                contact_page_forms = await self.analyze_all_forms_on_page(page, f"{dealer_name} Contact Page")
                                if contact_page_forms:
                                    best_contact_form = max(contact_page_forms, key=lambda x: x['contactLikelihood'])
                                    print(f"   📞 CONTACT PAGE FORM: {best_contact_form['contactLikelihood']}% likelihood")
                        except Exception:
                            pass

                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'status': 'universal_success',
                            'contact_forms_found': len(contact_forms),
                            'best_form_likelihood': best_form['contactLikelihood'],
                            'best_form_inputs': best_form['totalInputs'],
                            'screenshot_path': screenshot_path
                        }
                    else:
                        print(f"   ❌ No contact forms identified with universal analysis")
                        result = {
                            'dealer_name': dealer_name,
                            'website': website,
                            'status': 'universal_failed',
                            'contact_forms_found': 0
                        }

                    results.append(result)

                except Exception as e:
                    print(f"   ❌ Universal analysis error: {e}")
                    results.append({
                        'dealer_name': dealer_name,
                        'website': website,
                        'status': 'error',
                        'error': str(e)
                    })
                finally:
                    await context.close()

            await browser.close()

        # Save results
        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(output_dir, "universal_analysis_results.csv"), index=False)

        # Summary
        successful = len([r for r in results if r.get('status') == 'universal_success'])
        print(f"\n🎯 UNIVERSAL ANALYSIS COMPLETE!")
        print(f"✅ Success rate: {successful}/{len(failed_sites)} ({successful/len(failed_sites)*100:.1f}%)")
        print(f"📈 Final improvement: Previously 0/5 → Enhanced 2/5 → Universal {successful}/5")

        return results

if __name__ == "__main__":
    analyzer = UniversalFormAnalyzer()
    asyncio.run(analyzer.test_universal_analysis())