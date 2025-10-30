#!/usr/bin/env python3
"""
Live test of Cloudflare stealth capabilities with visible browser and detailed logging.
Tests the blocked dealership site to verify evasion techniques.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.browser.cloudflare_stealth_config import CloudflareStealth
from src.automation.forms.stealth_form_detector import StealthFormDetector, MinimalFormSubmissionPipeline
from src.automation.forms.human_form_filler import HumanFormFiller


class VisibleCloudflareTest:
    """Test Cloudflare evasion with visible progress and detailed logging."""

    def __init__(self):
        self.test_sites = [
            {
                'name': 'Capital City CDJR (Previously Blocked)',
                'url': 'https://www.capcitycdjr.com/contact-us/',
                'description': 'Site that was blocked in previous tests'
            },
            {
                'name': 'Test Site 2',
                'url': 'https://www.dealerconnection.com/contact/',
                'description': 'Alternative test site'
            }
        ]

        self.test_contact_data = {
            'first_name': 'Miguel',
            'last_name': 'Montoya',
            'email': 'migueljmontoya@protonmail.com',
            'phone': '650-688-2311',
            'message': 'Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available? Best, Miguel'
        }

    async def run_visible_test(self):
        """Run the full test with visible browser and step-by-step logging."""
        print("🎯 CLOUDFLARE STEALTH EVASION TEST")
        print("=" * 60)
        print("⚠️  BROWSER WILL OPEN - WATCH THE AUTOMATION IN ACTION")
        print("=" * 60)

        for i, site in enumerate(self.test_sites, 1):
            print(f"\n🔍 TEST {i}: {site['name']}")
            print(f"📍 URL: {site['url']}")
            print(f"📝 Description: {site['description']}")
            print("-" * 40)

            result = await self._test_single_site(site)

            print("\n📊 TEST RESULT:")
            if result['success']:
                print("✅ SUCCESS - Cloudflare evasion worked!")
            else:
                print("❌ FAILED - Still getting blocked")

            print(f"📋 Details: {result}")
            print("=" * 60)

            if i < len(self.test_sites):
                print("\n⏳ Waiting 5 seconds before next test...")
                await asyncio.sleep(5)

    async def _test_single_site(self, site_info: dict) -> dict:
        """Test a single site with detailed progress logging."""
        start_time = time.time()
        result = {
            'site': site_info['name'],
            'url': site_info['url'],
            'success': False,
            'stages_completed': [],
            'errors': [],
            'timings': {},
            'cloudflare_detected': False,
            'form_found': False,
            'form_filled': False,
            'submitted': False
        }

        stealth = CloudflareStealth()
        browser = None
        context = None

        try:
            # Stage 1: Browser Setup
            print("🚀 Stage 1: Setting up stealth browser...")
            stage_start = time.time()
            browser, context, page = await stealth.create_stealth_session()
            result['timings']['browser_setup'] = time.time() - stage_start
            result['stages_completed'].append('browser_setup')
            print(f"   ✅ Browser ready ({result['timings']['browser_setup']:.2f}s)")

            # Stage 2: Navigation with Cloudflare Evasion
            print("🌐 Stage 2: Navigating with Cloudflare evasion...")
            stage_start = time.time()
            navigation_success = await stealth.navigate_with_cloudflare_evasion(
                page, site_info['url'], max_wait_time=30000
            )
            result['timings']['navigation'] = time.time() - stage_start
            print(f"   🕒 Navigation time: {result['timings']['navigation']:.2f}s")

            if not navigation_success:
                result['errors'].append('Navigation failed or Cloudflare blocked')
                result['cloudflare_detected'] = True
                print("   ❌ Navigation failed - likely Cloudflare blocked")
                return result

            result['stages_completed'].append('navigation')
            print("   ✅ Navigation successful - Cloudflare bypassed!")

            # Stage 3: Check for blocking indicators
            print("🔍 Stage 3: Checking for security blocks...")
            body_text = await page.inner_text('body')
            blocked_indicators = [
                'sorry, you have been blocked',
                'cloudflare ray id',
                'blocked because your browser',
                'access denied',
                'why have i been blocked'
            ]

            blocked = any(indicator in body_text.lower() for indicator in blocked_indicators)
            if blocked:
                result['cloudflare_detected'] = True
                result['errors'].append('Security block page detected')
                print("   ❌ Security block page detected")

                # Take screenshot of block page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"blocked_page_{timestamp}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"   📸 Screenshot saved: {screenshot_path}")
                return result

            result['stages_completed'].append('security_check')
            print("   ✅ No security blocks detected")

            # Stage 4: Form Detection
            print("📝 Stage 4: Detecting contact form...")
            stage_start = time.time()
            detector = StealthFormDetector()
            form_result = await detector.detect_form_quickly(page)
            result['timings']['form_detection'] = time.time() - stage_start
            print(f"   🕒 Detection time: {result['timings']['form_detection']:.2f}s")

            if not form_result.success:
                result['errors'].append(f'Form detection failed: {form_result.detection_method}')
                print(f"   ❌ Form detection failed: {form_result.detection_method}")
                return result

            result['form_found'] = True
            result['stages_completed'].append('form_detection')
            print(f"   ✅ Form found! Method: {form_result.detection_method}")
            print(f"   📋 Fields detected: {list(form_result.fields.keys())}")

            # Stage 5: Human-like Form Filling
            print("✍️  Stage 5: Filling form with human-like behavior...")
            stage_start = time.time()

            human_filler = HumanFormFiller()
            filled_count = 0

            for field_name, field_info in form_result.fields.items():
                if field_name in self.test_contact_data:
                    print(f"   📝 Filling {field_name}...")
                    success = await human_filler.fill_field_naturally(
                        page,
                        field_info.selector,
                        self.test_contact_data[field_name],
                        field_name
                    )
                    if success:
                        filled_count += 1
                        print(f"      ✅ {field_name} filled successfully")
                    else:
                        print(f"      ❌ {field_name} failed to fill")

                    # Natural pause between fields
                    await human_filler.pause_between_fields(field_name)

            result['timings']['form_filling'] = time.time() - stage_start
            print(f"   🕒 Form filling time: {result['timings']['form_filling']:.2f}s")
            print(f"   📊 Fields filled: {filled_count}/{len(form_result.fields)}")

            if filled_count > 0:
                result['form_filled'] = True
                result['stages_completed'].append('form_filling')
                print("   ✅ Form filling completed successfully")
            else:
                result['errors'].append('No fields could be filled')
                print("   ❌ Form filling failed - no fields filled")
                return result

            # Stage 6: Take Screenshot Before Submission
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_submit_screenshot = f"form_filled_{timestamp}.png"
            await page.screenshot(path=pre_submit_screenshot, full_page=True)
            print(f"   📸 Pre-submission screenshot: {pre_submit_screenshot}")

            # Stage 7: Form Submission (Optional - can be skipped for testing)
            submit_form = input("\n🤔 Submit the form? (y/N): ").lower().startswith('y')

            if submit_form and form_result.submit_selector:
                print("📤 Stage 7: Submitting form...")
                stage_start = time.time()

                # Use human-like submission
                pipeline = MinimalFormSubmissionPipeline()
                submit_success = await pipeline._submit_form_quickly(page, form_result.submit_selector)

                result['timings']['submission'] = time.time() - stage_start

                if submit_success:
                    result['submitted'] = True
                    result['stages_completed'].append('submission')
                    print(f"   ✅ Form submitted successfully ({result['timings']['submission']:.2f}s)")

                    # Screenshot after submission
                    post_submit_screenshot = f"form_submitted_{timestamp}.png"
                    await page.screenshot(path=post_submit_screenshot, full_page=True)
                    print(f"   📸 Post-submission screenshot: {post_submit_screenshot}")
                else:
                    result['errors'].append('Form submission failed')
                    print("   ❌ Form submission failed")
            else:
                print("   ⏭️  Skipping form submission (testing only)")

            # Final success determination
            if result['form_found'] and result['form_filled']:
                result['success'] = True

        except Exception as exc:
            result['errors'].append(f'Unexpected error: {exc}')
            print(f"   💥 Unexpected error: {exc}")

        finally:
            # Cleanup
            print("🧹 Cleaning up browser session...")
            await stealth.close_session(browser, context)
            result['timings']['total'] = time.time() - start_time

        return result

    def print_summary(self, results: list):
        """Print a summary of all test results."""
        print("\n" + "=" * 60)
        print("📈 CLOUDFLARE EVASION TEST SUMMARY")
        print("=" * 60)

        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])

        print(f"🎯 Tests Run: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        print(f"📊 Success Rate: {(successful_tests/total_tests)*100:.1f}%")

        print("\n📋 Detailed Results:")
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"\n{i}. {result['site']}: {status}")
            print(f"   🔗 {result['url']}")
            print(f"   ⏱️  Total time: {result['timings'].get('total', 0):.2f}s")
            print(f"   🎬 Stages: {' → '.join(result['stages_completed'])}")
            if result['errors']:
                print(f"   ⚠️  Errors: {', '.join(result['errors'])}")

async def main():
    """Main test execution."""
    print("🔧 CLOUDFLARE STEALTH TEST STARTING...")
    print("📋 This test will open a visible browser window")
    print("👀 Watch the automation behavior to help troubleshoot")
    print("\nPress Ctrl+C to stop the test at any time\n")

    try:
        tester = VisibleCloudflareTest()
        await tester.run_visible_test()
        print("\n🏁 Test completed! Check the screenshots and results above.")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed with error: {exc}")

if __name__ == "__main__":
    asyncio.run(main())