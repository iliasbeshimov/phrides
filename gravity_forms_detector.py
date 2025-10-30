#!/usr/bin/env python3
"""
GRAVITY FORMS DETECTOR - Specialized detector for Gravity Forms
Based on analysis of failed sites - they all use Gravity Forms with standard patterns
"""

import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

class GravityFormsDetector:
    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()

    async def test_failed_sites_with_gravity_detection(self):
        test_sites = [
            {'name': 'Thomas Garage Inc', 'url': 'https://www.thomasautocenters.com/contact-us/'},
            {'name': 'Thomson Chrysler (Jeep Cheap)', 'url': 'https://www.jeepcheap.com/contact-us/'},
            {'name': 'Tilleman Motor Co', 'url': 'https://www.tillemanmotor.net/contact-us/'},
            {'name': 'Rairdon Chrysler Kirkland', 'url': 'https://www.dodgechryslerjeepofkirkland.com/contact-us/'},
            {'name': 'Tasca Chrysler White Plains', 'url': 'https://www.tascacdjrwhiteplains.com/contact-us/'},
        ]

        print("🎯 GRAVITY FORMS DETECTION TEST")
        print(f"🔍 Testing {len(test_sites)} sites with Gravity Forms")

        async with async_playwright() as p:
            browser, context = await self.browser_manager.open_context(p)

            try:
                for i, site in enumerate(test_sites):
                    print(f"\n🏪 #{i+1}: {site['name']}")
                    print(f"🌐 URL: {site['url']}")

                    page = await self.browser_manager.create_enhanced_stealth_page(context)

                    try:
                        await page.goto(site['url'], wait_until='domcontentloaded', timeout=30000)

                        # Smart waiting: Wait for actual content, not arbitrary time
                        try:
                            await page.wait_for_selector('.gform_wrapper, form', timeout=10000)
                        except:
                            # Fallback: wait for network idle if no forms immediately visible
                            await page.wait_for_load_state('networkidle', timeout=15000)

                    # Simple Gravity Forms detection
                    gforms = await page.locator('.gform_wrapper').count()
                    if gforms > 0:
                        print(f"   ✅ Found {gforms} Gravity Forms!")
                        
                        # Get form details
                        form_info = await page.evaluate("""
                            () => {
                                const gforms = document.querySelectorAll('.gform_wrapper form');
                                return Array.from(gforms).map((form, i) => {
                                    const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
                                    return {
                                        id: form.id,
                                        inputs: inputs.map(inp => ({
                                            name: inp.name,
                                            type: inp.type,
                                            label: inp.closest('li')?.querySelector('label')?.innerText || ''
                                        }))
                                    };
                                });
                            }
                        """)
                        
                        for j, form in enumerate(form_info):
                            print(f"      📋 Form {j+1}: {form['id']}")
                            for inp in form['inputs']:
                                if inp['type'] not in ['hidden', 'submit']:
                                    print(f"         - {inp['label']}: {inp['name']} ({inp['type']})")
                    else:
                        print(f"   ❌ No Gravity Forms found")

                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                    finally:
                        await page.close()

            finally:
                await self.browser_manager.close_context(browser, context)

if __name__ == "__main__":
    detector = GravityFormsDetector()
    asyncio.run(detector.test_failed_sites_with_gravity_detection())
