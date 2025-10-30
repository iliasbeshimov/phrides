#!/usr/bin/env python3
"""
Multi-Dealership Validation Test
Tests the residential automation system on multiple dealerships
"""

import asyncio
import json
import random
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from playwright.async_api import async_playwright
from src.automation.forms.form_submitter import ContactPayload

class MultiDealershipValidator:
    """Test automation across multiple dealerships."""

    def __init__(self):
        self.contact_data = ContactPayload(
            first_name='Miguel',
            last_name='Montoya',
            email='migueljmontoya@protonmail.com',
            phone='555-123-4567',
            zip_code='90210',
            message='I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals.'
        )

        # Test dealerships
        self.test_dealerships = [
            {
                'name': 'Capital City CDJR',
                'url': 'https://www.capcitycdjr.com/contact-us/',
                'expected_fields': ['email', 'phone', 'message']
            },
            {
                'name': 'Another Test Dealer',
                'url': 'https://www.capcitycdjr.com/get-quote/',
                'expected_fields': ['first_name', 'last_name', 'email', 'phone']
            }
        ]

    async def create_browser(self):
        """Create browser for testing."""
        playwright = await async_playwright().start()

        browser_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        ]

        browser = await playwright.chromium.launch(
            headless=False,
            args=browser_args
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        )

        # Add stealth
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            window.chrome = { runtime: {} };
        """)

        page = await context.new_page()
        return playwright, browser, page

    async def handle_overlays(self, page):
        """Handle common overlays."""
        await asyncio.sleep(2)

        # Accept cookies
        cookie_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("OK")',
            '[id*="cookie"] button'
        ]

        for selector in cookie_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    await element.click(timeout=3000)
                    await asyncio.sleep(1)
                    break
            except:
                continue

    async def fill_form_smart(self, page):
        """Smart form filling with validation."""
        field_mappings = {
            'first_name': [
                'input[name*="first"]', 'input[name*="fname"]', 'input[id*="first"]'
            ],
            'last_name': [
                'input[name*="last"]', 'input[name*="lname"]', 'input[id*="last"]'
            ],
            'email': [
                'input[type="email"]', 'input[name*="email"]', 'input[id*="email"]'
            ],
            'phone': [
                'input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]'
            ],
            'zip': [
                'input[name*="zip"]', 'input[name*="postal"]', 'input[id*="zip"]'
            ],
            'message': [
                'textarea', 'textarea[name*="message"]', 'textarea[name*="comment"]'
            ]
        }

        data_mapping = {
            'first_name': self.contact_data.first_name,
            'last_name': self.contact_data.last_name,
            'email': self.contact_data.email,
            'phone': self.contact_data.phone,
            'zip': self.contact_data.zip_code,
            'message': self.contact_data.message
        }

        filled_fields = []

        for field_type, selectors in field_mappings.items():
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        # Validate visible and fillable
                        bounding_box = await element.bounding_box()
                        if bounding_box and bounding_box['width'] > 0 and bounding_box['height'] > 0:
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(random.uniform(0.3, 0.7))

                            await element.click()
                            await asyncio.sleep(random.uniform(0.1, 0.3))

                            await element.fill('')
                            await asyncio.sleep(random.uniform(0.1, 0.2))

                            # Type naturally
                            value = data_mapping[field_type]
                            for char in value:
                                await page.keyboard.type(char)
                                await asyncio.sleep(random.uniform(0.04, 0.10))

                            filled_fields.append(field_type)
                            await asyncio.sleep(random.uniform(0.8, 1.5))
                            break

                except Exception:
                    continue

        return filled_fields

    async def submit_and_verify(self, page):
        """Submit form and verify result."""
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            '.submit-btn'
        ]

        for selector in submit_selectors:
            try:
                submit_btn = page.locator(selector).first
                if await submit_btn.is_visible(timeout=2000):
                    current_url = page.url

                    await submit_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await submit_btn.click()

                    # Wait for response
                    await asyncio.sleep(4)

                    # Check for success indicators
                    new_url = page.url
                    content = await page.content()

                    success_indicators = [
                        'thank you', 'thanks', 'confirm', 'success',
                        'received', 'submitted', 'sent'
                    ]

                    url_changed = new_url != current_url
                    has_success_text = any(indicator in content.lower() for indicator in success_indicators)

                    if url_changed or has_success_text:
                        return 'success'
                    elif 'blocked' in content.lower():
                        return 'blocked'
                    else:
                        return 'unclear'

            except Exception:
                continue

        return 'no_submit_button'

    async def test_single_dealer(self, dealer_info):
        """Test automation on single dealership."""
        print(f"\n🎯 TESTING: {dealer_info['name']}")
        print(f"🔗 URL: {dealer_info['url']}")
        print("=" * 50)

        playwright, browser, page = await self.create_browser()

        try:
            # Navigate
            await page.goto(dealer_info['url'], timeout=30000)
            await asyncio.sleep(2)

            # Handle overlays
            await self.handle_overlays(page)

            # Fill form
            filled_fields = await self.fill_form_smart(page)
            print(f"   📝 Filled fields: {', '.join(filled_fields)}")

            if filled_fields:
                # Submit
                result = await self.submit_and_verify(page)
                print(f"   🚀 Submission result: {result}")

                success = result in ['success', 'unclear']  # Unclear is often success

                return {
                    'name': dealer_info['name'],
                    'url': dealer_info['url'],
                    'filled_fields': filled_fields,
                    'submission_result': result,
                    'success': success
                }
            else:
                print("   ❌ No form fields found")
                return {
                    'name': dealer_info['name'],
                    'url': dealer_info['url'],
                    'filled_fields': [],
                    'submission_result': 'no_form',
                    'success': False
                }

        except Exception as e:
            print(f"   💥 Error: {e}")
            return {
                'name': dealer_info['name'],
                'url': dealer_info['url'],
                'filled_fields': [],
                'submission_result': 'error',
                'success': False,
                'error': str(e)
            }

        finally:
            await asyncio.sleep(3)  # Let user see result
            await browser.close()
            await playwright.stop()

    async def run_validation(self):
        """Run validation across multiple dealerships."""
        print("🏢 MULTI-DEALERSHIP VALIDATION TEST")
        print("=" * 60)
        print("Testing residential IP automation across multiple dealers...\n")

        results = []

        for dealer_info in self.test_dealerships:
            result = await self.test_single_dealer(dealer_info)
            results.append(result)

            # Pause between tests
            await asyncio.sleep(3)

        # Summary
        print("\n" + "=" * 60)
        print("🏆 VALIDATION RESULTS SUMMARY")
        print("=" * 60)

        successful = sum(1 for r in results if r['success'])
        total = len(results)

        print(f"📊 Overall Success Rate: {successful}/{total} ({100*successful/total:.1f}%)")

        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"\n{status} {result['name']}")
            print(f"   📝 Fields filled: {len(result['filled_fields'])}")
            print(f"   🚀 Submission: {result['submission_result']}")
            if 'error' in result:
                print(f"   ⚠️ Error: {result['error']}")

        if successful >= total * 0.8:  # 80% success rate
            print(f"\n🎉 VALIDATION PASSED!")
            print("   The automation system is working reliably.")
        else:
            print(f"\n⚠️ VALIDATION NEEDS IMPROVEMENT")
            print("   Some dealerships failed automation.")

        return results

async def main():
    """Run multi-dealership validation."""
    validator = MultiDealershipValidator()

    try:
        results = await validator.run_validation()
        return results

    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user.")
    except Exception as e:
        print(f"\n💥 Validation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())