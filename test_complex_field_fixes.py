"""
Test script for complex field fixes:
1. David Stanley Dodge LLC - split phone field
2. Faws Garage - split phone field
3. Fillback Chrysler - Gravity Forms with complex name and zip code
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler
from src.utils.logging import get_logger

logger = get_logger(__name__)


TEST_DEALERSHIPS = [
    {
        "name": "David Stanley Dodge LLC",
        "website": "https://www.davidstanleychryslerjeepdodgeofoklahoma.com",
        "contact_url": "https://www.davidstanleychryslerjeepdodgeofoklahoma.com/contact-us/",
        "issue": "Split phone field"
    },
    {
        "name": "Faws Garage",
        "website": "https://www.fawsgaragecdjr.com",
        "contact_url": "https://www.fawsgaragecdjr.com/contact-us/",
        "issue": "Split phone field"
    },
    {
        "name": "Fillback Chrysler, Dodge, Jeep & Ram",
        "website": "https://www.fillbackprairieduchiencdjr.com",
        "contact_url": "https://www.fillbackprairieduchiencdjr.com/contact-us/",
        "issue": "Gravity Forms complex name + zip code"
    }
]


TEST_DATA = {
    "first_name": "Miguel",
    "last_name": "Montoya",
    "email": "miguelpmontoya@protonmail.com",
    "phone": "6501234567",
    "zip_code": "94025",
    "message": "Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"
}


async def test_dealership(dealership: dict) -> dict:
    """Test a single dealership with complex field handling"""

    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {dealership['name']}")
    logger.info(f"Issue: {dealership['issue']}")
    logger.info(f"URL: {dealership['contact_url']}")
    logger.info(f"{'='*80}\n")

    result = {
        "dealer_name": dealership["name"],
        "website": dealership["website"],
        "issue": dealership["issue"],
        "form_detected": False,
        "complex_fields_detected": [],
        "fields_filled": [],
        "success": False,
        "error": None
    }

    browser = None
    playwright_instance = None

    try:
        # Create stealth browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Navigate to contact page
        logger.info(f"Navigating to {dealership['contact_url']}")
        await page.goto(dealership['contact_url'], wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        # Initialize detectors
        form_detector = EnhancedFormDetector()
        complex_handler = ComplexFieldHandler()

        # Detect form
        logger.info("Detecting form...")
        form_result = await form_detector.detect_contact_form(page)

        if not form_result.success:
            result["error"] = "No form detected"
            logger.error("Form detection failed")
            return result

        result["form_detected"] = True
        logger.info(f"Form detected with {len(form_result.fields)} standard fields")

        # Detect complex fields
        logger.info("Checking for complex fields...")

        # Check for split phone field
        split_phone = await complex_handler.detect_split_phone_field(page)
        if split_phone:
            result["complex_fields_detected"].append("split_phone")
            logger.info("✓ Split phone field detected")

            # Fill split phone field
            success = await complex_handler.fill_split_phone_field(split_phone, TEST_DATA["phone"])
            if success:
                result["fields_filled"].append("phone_split")
                logger.info("✓ Split phone field filled")

        # Check for complex name field
        complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
        if complex_name:
            result["complex_fields_detected"].append("complex_name")
            logger.info("✓ Complex name field detected")

            # Fill complex name field
            success = await complex_handler.fill_complex_name_field(
                complex_name,
                TEST_DATA["first_name"],
                TEST_DATA["last_name"]
            )
            if success:
                result["fields_filled"].append("name_complex")
                logger.info("✓ Complex name field filled")

        # Check for Gravity Forms zip code
        gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)
        if gravity_zip:
            result["complex_fields_detected"].append("gravity_zip")
            logger.info("✓ Gravity Forms zip code detected")

            # Fill zip code
            try:
                await gravity_zip.fill(TEST_DATA["zip_code"])
                result["fields_filled"].append("zip_gravity")
                logger.info("✓ Gravity Forms zip code filled")
            except Exception as e:
                logger.error(f"Failed to fill gravity zip: {str(e)}")

        # Fill remaining standard fields
        logger.info("Filling remaining standard fields...")

        for field_type, field_info in form_result.fields.items():
            # Skip fields already handled by complex handlers
            if field_type in ["phone"] and "split_phone" in result["complex_fields_detected"]:
                continue
            if field_type in ["first_name", "last_name"] and "complex_name" in result["complex_fields_detected"]:
                continue
            if field_type in ["zip"] and "gravity_zip" in result["complex_fields_detected"]:
                continue

            # Map field types to test data
            value = None
            if field_type == "first_name":
                value = TEST_DATA["first_name"]
            elif field_type == "last_name":
                value = TEST_DATA["last_name"]
            elif field_type == "email":
                value = TEST_DATA["email"]
            elif field_type == "phone":
                value = TEST_DATA["phone"]
            elif field_type in ["zip", "zip_code"]:
                value = TEST_DATA["zip_code"]
            elif field_type == "message":
                value = TEST_DATA["message"]

            if value:
                try:
                    await field_info.element.fill(value)
                    result["fields_filled"].append(field_type)
                    logger.info(f"✓ Filled {field_type}")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.error(f"Failed to fill {field_type}: {str(e)}")

        # Take screenshot
        screenshot_dir = Path("tests/complex_field_test")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshot_dir / f"{dealership['name'].replace(' ', '_')}_{timestamp}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")

        result["success"] = len(result["fields_filled"]) > 0

        # Wait for manual inspection
        logger.info("\n" + "="*80)
        logger.info("FORM FILLED - Press Enter to continue to next dealership...")
        logger.info("="*80)
        input()

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        result["error"] = str(e)

    finally:
        if browser:
            try:
                await browser.close()
                await playwright_instance.stop()
            except:
                pass

    return result


async def main():
    """Run tests on all problem dealerships"""

    logger.info("\n" + "="*80)
    logger.info("COMPLEX FIELD FIXES TEST")
    logger.info("Testing 3 dealerships with complex field issues")
    logger.info("="*80 + "\n")

    results = []

    for dealership in TEST_DEALERSHIPS:
        result = await test_dealership(dealership)
        results.append(result)
        await asyncio.sleep(2)

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*80 + "\n")

    for result in results:
        logger.info(f"\n{result['dealer_name']}")
        logger.info(f"  Issue: {result['issue']}")
        logger.info(f"  Form Detected: {result['form_detected']}")
        logger.info(f"  Complex Fields: {', '.join(result['complex_fields_detected']) if result['complex_fields_detected'] else 'None'}")
        logger.info(f"  Fields Filled: {', '.join(result['fields_filled']) if result['fields_filled'] else 'None'}")
        logger.info(f"  Success: {'✓' if result['success'] else '✗'}")
        if result['error']:
            logger.info(f"  Error: {result['error']}")

    logger.info("\n" + "="*80)
    logger.info(f"Overall: {sum(1 for r in results if r['success'])}/{len(results)} successful")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
