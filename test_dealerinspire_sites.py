#!/usr/bin/env python3
"""
Test script specifically for the 4 failed DealerInspire sites
to validate the Cloudflare bypass strategy works.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.browser.dealerinspire_bypass import apply_dealerinspire_bypass, DealerInspireBypass


# The 4 failed DealerInspire sites from previous test
DEALERINSPIRE_SITES = [
    {
        'name': 'Reagle Chrysler Dodge Jeep Ram',
        'website': 'https://www.reagledodge.net',
        'contact_url': 'https://www.reagledodge.net/contact-us/',
    },
    {
        'name': 'Downtown Auto Group Inc',
        'website': 'https://www.buydowntown.com',
        'contact_url': 'https://www.buydowntown.com/contact-us/',
    },
    {
        'name': 'Miracle Chrysler Dodge Jeep Ram',
        'website': 'https://www.miraclecdjrofaiken.com',
        'contact_url': 'https://www.miraclecdjrofaiken.com/contact-us/',
    },
    {
        'name': 'Swope Chrysler Dodge Jeep',
        'website': 'https://www.swopechryslerdodgejeep.com',
        'contact_url': 'https://www.swopechryslerdodgejeep.com/contact-us/',
    },
]


class DealerInspireBypassTester:
    """Test the DealerInspire bypass strategy"""

    def __init__(self):
        self.browser_manager = EnhancedStealthBrowserManager()
        self.results = []

        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"tests/dealerinspire_test_{timestamp}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def test_site(self, context, site_info):
        """Test a single DealerInspire site"""

        dealer_name = site_info['name']
        contact_url = site_info['contact_url']

        print(f"\n{'='*80}")
        print(f"🏪 Testing: {dealer_name}")
        print(f"🔗 URL: {contact_url}")
        print(f"{'='*80}")

        page = await self.browser_manager.create_enhanced_stealth_page(context)

        result = {
            'dealer_name': dealer_name,
            'contact_url': contact_url,
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'is_dealerinspire': False,
            'cloudflare_detected': False,
            'forms_found': 0,
            'gravity_forms_found': 0,
            'error': None,
        }

        try:
            # Step 1: Apply DealerInspire bypass
            print(f"\n   🚀 Applying DealerInspire bypass...")
            bypass_success = await apply_dealerinspire_bypass(page, contact_url)

            if not bypass_success:
                result['error'] = "Bypass failed"
                result['status'] = 'bypass_failed'
                return result

            print(f"   ✅ Bypass completed")

            # Step 2: Check if DealerInspire detected
            is_di = await DealerInspireBypass.detect_dealerinspire(page)
            result['is_dealerinspire'] = is_di
            if is_di:
                print(f"   🔍 DealerInspire software confirmed")

            # Step 3: Check if still blocked by Cloudflare
            is_blocked = await DealerInspireBypass.detect_and_handle_cloudflare_block(page)
            result['cloudflare_detected'] = is_blocked
            if is_blocked:
                print(f"   ⚠️  Still blocked by Cloudflare")
                result['error'] = "Cloudflare block persists"
                result['status'] = 'blocked'
                return result

            print(f"   ✅ No Cloudflare block detected")

            # Step 4: Wait for forms to load
            await asyncio.sleep(2)

            # Step 5: Count forms
            all_forms = await page.locator('form').all()
            result['forms_found'] = len(all_forms)
            print(f"   📋 Found {len(all_forms)} forms")

            # Step 6: Count Gravity Forms specifically
            gravity_forms = await page.locator('.gform_wrapper').all()
            result['gravity_forms_found'] = len(gravity_forms)
            print(f"   📋 Found {len(gravity_forms)} Gravity Forms")

            # Step 7: Take screenshots
            screenshot_path = self.output_dir / f"{dealer_name.lower().replace(' ', '_')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            result['screenshot_path'] = str(screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")

            # Step 8: Get page HTML snippet for verification
            html_snippet = await page.content()

            # Check for form elements in HTML
            has_input = 'type="email"' in html_snippet or 'name="email"' in html_snippet.lower()
            has_textarea = '<textarea' in html_snippet.lower()
            has_submit = 'type="submit"' in html_snippet or 'submit' in html_snippet.lower()

            print(f"   📄 HTML analysis:")
            print(f"      - Email inputs: {has_input}")
            print(f"      - Textareas: {has_textarea}")
            print(f"      - Submit buttons: {has_submit}")

            # Step 9: Determine success
            if result['forms_found'] > 0:
                result['status'] = 'success'
                print(f"\n   ✅ SUCCESS: Forms detected on {dealer_name}")
            else:
                result['status'] = 'no_forms'
                result['error'] = "No forms found after bypass"
                print(f"\n   ⚠️  WARNING: No forms found after bypass")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            result['error'] = str(e)
            result['status'] = 'error'

        finally:
            await page.close()

        self.results.append(result)
        return result

    async def run_all_tests(self):
        """Run tests on all DealerInspire sites"""

        print(f"\n{'='*80}")
        print(f"DEALERINSPIRE CLOUDFLARE BYPASS TEST")
        print(f"Testing {len(DEALERINSPIRE_SITES)} previously failed sites")
        print(f"{'='*80}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await self.browser_manager.create_enhanced_stealth_context(browser)

            for site_info in DEALERINSPIRE_SITES:
                await self.test_site(context, site_info)

            await context.close()
            await browser.close()

        # Print summary
        self._print_summary()

        # Save results
        self._save_results()

    def _print_summary(self):
        """Print test summary"""

        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")

        total = len(self.results)
        success = len([r for r in self.results if r['status'] == 'success'])
        blocked = len([r for r in self.results if r['status'] == 'blocked'])
        no_forms = len([r for r in self.results if r['status'] == 'no_forms'])
        errors = len([r for r in self.results if r['status'] == 'error'])

        print(f"\n📊 Overall Results:")
        print(f"   Total sites tested: {total}")
        print(f"   ✅ Success (forms found): {success} ({success/total*100:.1f}%)")
        print(f"   🚫 Still blocked: {blocked} ({blocked/total*100:.1f}%)")
        print(f"   ⚠️  No forms found: {no_forms} ({no_forms/total*100:.1f}%)")
        print(f"   ❌ Errors: {errors} ({errors/total*100:.1f}%)")

        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status_icon = {
                'success': '✅',
                'blocked': '🚫',
                'no_forms': '⚠️',
                'error': '❌',
                'bypass_failed': '❌',
            }.get(result['status'], '❓')

            print(f"   {status_icon} {result['dealer_name']}")
            print(f"      Status: {result['status']}")
            print(f"      Forms found: {result['forms_found']}")
            print(f"      Gravity Forms: {result['gravity_forms_found']}")
            if result.get('error'):
                print(f"      Error: {result['error']}")
            print()

    def _save_results(self):
        """Save results to JSON"""

        results_file = self.output_dir / "results.json"

        with open(results_file, 'w') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'total_sites': len(self.results),
                'success_count': len([r for r in self.results if r['status'] == 'success']),
                'results': self.results,
            }, f, indent=2)

        print(f"💾 Results saved to: {results_file}")


async def main():
    """Main entry point"""
    tester = DealerInspireBypassTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
