#!/usr/bin/env python3
"""
Simple test using existing EnhancedStealthBrowserManager to test Cloudflare evasion.
This will use the existing codebase to avoid dependency issues.
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

# Import existing modules
from enhanced_stealth_browser_config import EnhancedStealthBrowserManager
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from playwright.async_api import async_playwright


class SimpleCloudflareTest:
    """Simple test using existing enhanced stealth browser."""

    def __init__(self):
        self.test_url = "https://www.capcitycdjr.com/contact-us/"
        self.browser_manager = EnhancedStealthBrowserManager()
        self.form_detector = EnhancedFormDetector()

    async def run_test(self):
        """Run test with detailed progress logging."""
        print("🎯 SIMPLE CLOUDFLARE EVASION TEST")
        print("=" * 50)
        print(f"🔍 Testing: {self.test_url}")
        print("⚠️  BROWSER WILL OPEN - WATCH FOR CLOUDFLARE BEHAVIOR")
        print("=" * 50)

        start_time = time.time()

        async with async_playwright() as playwright:
            try:
                print("\n🚀 Stage 1: Setting up enhanced stealth browser...")
                browser, context = await self.browser_manager.open_context(
                    playwright, headless=False  # Visible browser for debugging
                )
                page = await self.browser_manager.create_enhanced_stealth_page(context)
                print("   ✅ Browser ready with enhanced stealth configuration")

                print("\n🌐 Stage 2: Navigating to target site...")
                navigation_start = time.time()

                try:
                    response = await page.goto(
                        self.test_url,
                        wait_until="domcontentloaded",
                        timeout=30000
                    )
                    navigation_time = time.time() - navigation_start
                    print(f"   ✅ Navigation completed ({navigation_time:.2f}s)")
                    print(f"   📄 Status: {response.status if response else 'Unknown'}")

                except Exception as nav_error:
                    print(f"   ❌ Navigation failed: {nav_error}")
                    return

                print("\n⏳ Stage 3: Waiting for page to settle...")
                await asyncio.sleep(3)  # Give time for any CF challenges

                print("\n🔍 Stage 4: Checking for security blocks...")
                try:
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
                        print("   ❌ BLOCKED - Cloudflare security page detected")

                        # Take screenshot of block page
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"blocked_page_{timestamp}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"   📸 Block page screenshot: {screenshot_path}")

                        # Print some of the block page content for analysis
                        title = await page.title()
                        print(f"   📄 Page title: {title}")
                        print(f"   📄 Body preview: {body_text[:200]}...")

                        return {"success": False, "blocked": True}
                    else:
                        print("   ✅ SUCCESS - No security blocks detected!")

                        # Take screenshot of success
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"success_page_{timestamp}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"   📸 Success screenshot: {screenshot_path}")

                        title = await page.title()
                        print(f"   📄 Page title: {title}")

                except Exception as check_error:
                    print(f"   ⚠️  Error checking page content: {check_error}")

                print("\n📝 Stage 5: Quick form detection test...")
                try:
                    detection_start = time.time()
                    form_result = await self.form_detector.detect_contact_form(page)
                    detection_time = time.time() - detection_start

                    if form_result.success:
                        print(f"   ✅ Form detected successfully ({detection_time:.2f}s)")
                        print(f"   📋 Fields found: {len(form_result.fields)}")
                        print(f"   🎯 Confidence: {form_result.confidence_score:.2f}")
                    else:
                        print(f"   ⚠️  Form detection failed ({detection_time:.2f}s)")

                except Exception as form_error:
                    print(f"   ⚠️  Form detection error: {form_error}")

                total_time = time.time() - start_time
                print(f"\n⏱️  Total test time: {total_time:.2f}s")

                print("\n🎉 TEST COMPLETED SUCCESSFULLY!")
                print("👀 Check the browser window and screenshots")

                # Keep browser open for 10 seconds for manual inspection
                print("\n⏳ Keeping browser open for 10 seconds for inspection...")
                await asyncio.sleep(10)

                return {"success": True, "blocked": False}

            except Exception as test_error:
                print(f"\n💥 Test failed with error: {test_error}")
                return {"success": False, "error": str(test_error)}

            finally:
                print("\n🧹 Cleaning up...")
                try:
                    await self.browser_manager.close_context(browser, context)
                except:
                    pass

async def main():
    """Main test execution."""
    print("🔧 STARTING SIMPLE CLOUDFLARE TEST...")
    print("📋 This test will open a visible browser window")
    print("👀 Watch for Cloudflare challenges or blocking")
    print("\nPress Ctrl+C to stop the test\n")

    try:
        tester = SimpleCloudflareTest()
        result = await tester.run_test()

        if result and result.get("success"):
            print("\n🎯 RESULT: Cloudflare evasion SUCCESSFUL! ✅")
        else:
            print("\n🎯 RESULT: Cloudflare blocking detected ❌")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as exc:
        print(f"\n💥 Test failed: {exc}")

if __name__ == "__main__":
    asyncio.run(main())