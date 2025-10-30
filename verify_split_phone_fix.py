"""Quick verification test for split phone fix on David Stanley and Faws Garage"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.complex_field_handler import ComplexFieldHandler

TEST_SITES = [
    {
        "name": "David Stanley Dodge LLC",
        "url": "https://www.davidstanleychryslerjeepdodgeofoklahoma.com/contact-us/"
    },
    {
        "name": "Faws Garage",
        "url": "https://www.fawsgaragecdjr.com/contact-us/"
    }
]

async def test_site(site):
    print(f"\n{'='*80}")
    print(f"Testing: {site['name']}")
    print(f"URL: {site['url']}")
    print('='*80)

    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

    try:
        print(f"Navigating...")
        await page.goto(site['url'], wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        # Test split phone detection
        print("Detecting split phone field...")
        handler = ComplexFieldHandler()
        split_phone = await handler.detect_split_phone_field(page)

        if split_phone:
            print(f"✅ DETECTED split phone field!")
            print(f"   Area code selector: {split_phone.area_code_selector}")
            print(f"   Prefix selector: {split_phone.prefix_selector}")
            print(f"   Suffix selector: {split_phone.suffix_selector}")

            # Try to fill it
            print("\nFilling split phone field with: 6501234567")
            success = await handler.fill_split_phone_field(split_phone, "6501234567")

            if success:
                print("✅ SUCCESSFULLY FILLED split phone field!")

                # Take screenshot
                await page.screenshot(path=f"tests/{site['name'].replace(' ', '_')}_split_phone_SUCCESS.png", full_page=True)
                print(f"Screenshot saved: tests/{site['name'].replace(' ', '_')}_split_phone_SUCCESS.png")

                # Wait to see result
                await asyncio.sleep(3)
                return True
            else:
                print("❌ FAILED to fill split phone field")
                return False
        else:
            print("❌ FAILED to detect split phone field")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    finally:
        await browser.close()
        await playwright_instance.stop()

async def main():
    print("\n" + "="*80)
    print("SPLIT PHONE FIX VERIFICATION TEST")
    print("="*80)

    results = {}
    for site in TEST_SITES:
        results[site['name']] = await test_site(site)
        await asyncio.sleep(2)

    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{name}: {status}")

    total_success = sum(1 for s in results.values() if s)
    print(f"\nOverall: {total_success}/{len(results)} sites working")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
