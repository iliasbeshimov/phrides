"""Test Jimmy Britt zip code fix"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector

async def test_jimmy_britt():
    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

    try:
        print("Testing Jimmy Britt Chrysler Jeep Dodge Ram")
        print("URL: https://www.jbchryslerjeepdodgeram.com/contact.htm\n")

        await page.goto("https://www.jbchryslerjeepdodgeram.com/contact.htm",
                       wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        # Detect form
        detector = EnhancedFormDetector()
        result = await detector.detect_contact_form(page)

        print(f"Form detected: {result.success}")
        print(f"Fields found: {len(result.fields)}\n")

        # Check zip field
        if 'zip' in result.fields:
            zip_field = result.fields['zip']
            print(f"✓ Zip field detected")
            print(f"  Selector: {zip_field.selector}")

            # Try to fill it
            print(f"\nFilling zip code with: 94025")
            try:
                await zip_field.element.fill("94025")
                print("✓ Zip code filled successfully!")

                await asyncio.sleep(2)

                # Verify it was filled
                value = await zip_field.element.input_value()
                print(f"  Verified value: '{value}'")

                if value == "94025":
                    print("\n✅ SUCCESS: Zip code correctly filled!")
                    success = True
                else:
                    print(f"\n❌ FAILED: Expected '94025', got '{value}'")
                    success = False

            except Exception as e:
                print(f"❌ FAILED to fill: {str(e)}")
                success = False

            # Screenshot
            await page.screenshot(path="tests/jimmy_britt_zipcode_FIXED.png", full_page=True)
            print(f"\nScreenshot: tests/jimmy_britt_zipcode_FIXED.png")

        else:
            print("❌ Zip field NOT detected")
            success = False

        await asyncio.sleep(3)
        return success

    finally:
        await browser.close()
        await playwright_instance.stop()

if __name__ == "__main__":
    result = asyncio.run(test_jimmy_britt())
    print(f"\n{'='*80}")
    print(f"Final result: {'✅ WORKING' if result else '❌ FAILED'}")
    print('='*80)
