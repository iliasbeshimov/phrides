#!/usr/bin/env python3
"""
DEBUG DIRECT CONTACT TEST - Test direct contact URLs we know work
"""

import asyncio
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

class DirectContactTester:
    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()

    async def test_direct_contact_urls(self):
        # Direct contact URLs we know have forms
        direct_urls = [
            {'name': 'Thomas Garage Inc', 'url': 'https://www.thomasautocenters.com/contact-us/'},
            {'name': 'Thomson Chrysler', 'url': 'https://www.jeepcheap.com/contact-us/'},
            {'name': 'Tilleman Motor Co', 'url': 'https://www.tillemanmotor.net/contact-us/'},
            {'name': 'Rairdon\'s Chrysler', 'url': 'https://www.dodgechryslerjeepofkirkland.com/contact-us/'},
            {'name': 'Tasca Chrysler', 'url': 'https://www.tascacdjrwhiteplains.com/contact-us/'}
        ]

        print(f"🔍 DIRECT CONTACT URL TEST")
        print(f"Testing {len(direct_urls)} direct contact URLs")

        async with async_playwright() as p:
            browser, context = await self.browser_manager.open_context(p)

            try:
                for i, site in enumerate(direct_urls):
                    print(f"\n🏪 #{i+1}: {site['name']}")
                    print(f"🌐 URL: {site['url']}")

                    page = await self.browser_manager.create_enhanced_stealth_page(context)

                    try:
                        await page.goto(site['url'], wait_until='domcontentloaded', timeout=30000)
                        await page.wait_for_timeout(8000)

                    # Check basic page state
                    title = await page.title()
                    print(f"   📄 Page title: {title}")

                    # Simple Gravity Forms check
                    gforms = await page.locator('.gform_wrapper').count()
                    print(f"   📋 Gravity Forms found: {gforms}")

                    # Check if forms are present at all
                    all_forms = await page.locator('form').count()
                    print(f"   📝 All forms found: {all_forms}")

                    if gforms > 0:
                        # Get detailed Gravity Forms info
                        gform_details = await page.evaluate("""
                            () => {
                                const gforms = document.querySelectorAll('.gform_wrapper');
                                return Array.from(gforms).map((wrapper, i) => {
                                    const form = wrapper.querySelector('form');
                                    const inputs = Array.from(form?.querySelectorAll('input, textarea') || []);
                                    return {
                                        wrapperVisible: wrapper.offsetParent !== null,
                                        formId: form?.id || 'no-id',
                                        inputCount: inputs.length,
                                        visibleInputs: inputs.filter(inp => inp.offsetParent !== null).length,
                                        inputNames: inputs.map(inp => inp.name).filter(n => n && !n.includes('1337') && !n.includes('hidden'))
                                    };
                                });
                            }
                        """)

                        for j, gf in enumerate(gform_details):
                            print(f"      📋 GForm {j+1}: {gf['formId']}")
                            print(f"         Wrapper visible: {gf['wrapperVisible']}")
                            print(f"         {gf['visibleInputs']}/{gf['inputCount']} inputs visible")
                            print(f"         Input names: {gf['inputNames'][:5]}")

                    else:
                        print(f"   ❌ No Gravity Forms detected")

                    # Check for any forms at all
                    if all_forms > 0:
                        form_details = await page.evaluate("""
                            () => {
                                const forms = document.querySelectorAll('form');
                                return Array.from(forms).map((form, i) => ({
                                    id: form.id,
                                    visible: form.offsetParent !== null,
                                    inputCount: form.querySelectorAll('input, textarea').length
                                }));
                            }
                        """)
                        
                        print(f"   📝 All forms:")
                        for j, form in enumerate(form_details):
                            print(f"      Form {j+1}: {form['id']}, visible: {form['visible']}, inputs: {form['inputCount']}")

                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                    finally:
                        await page.close()

            finally:
                await self.browser_manager.close_context(browser, context)

if __name__ == "__main__":
    tester = DirectContactTester()
    asyncio.run(tester.test_direct_contact_urls())
