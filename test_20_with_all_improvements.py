"""
Comprehensive test with ALL improvements:
1. Complex field detection (split phone, gravity forms)
2. Enhanced submission with verification
3. CAPTCHA tracking for manual follow-up
4. Improved selector strategy
"""

import asyncio
import csv
import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler
from src.automation.forms.enhanced_form_submitter import EnhancedFormSubmitter
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.services.captcha_tracker import CaptchaTracker
from src.utils.logging import get_logger

logger = get_logger(__name__)


TEST_DATA = {
    "first_name": "Miguel",
    "last_name": "Montoya",
    "email": "miguelpmontoya@protonmail.com",
    "phone": "6501234567",
    "zip_code": "94025",
    "message": "Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"
}


def load_dealerships(csv_file: str = "Dealerships.csv") -> List[Dict]:
    """Load dealerships from CSV"""
    dealerships = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dealerships.append({
                "dealer_name": row.get("dealer_name", ""),
                "website": row.get("website", ""),
                "city": row.get("city", ""),
                "state": row.get("state", "")
            })

    return dealerships


def select_random_dealerships(dealerships: List[Dict], count: int, exclude: List[str] = []) -> List[Dict]:
    """Select random dealerships excluding previously tested ones"""

    available = [d for d in dealerships if d["website"] not in exclude]
    return random.sample(available, min(count, len(available)))


async def test_dealership(dealership: Dict, test_dir: Path, captcha_tracker: CaptchaTracker) -> Dict:
    """Test single dealership with all improvements"""

    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {dealership['dealer_name']}")
    logger.info(f"Website: {dealership['website']}")
    logger.info(f"{'='*80}\n")

    result = {
        "dealer_name": dealership["dealer_name"],
        "website": dealership["website"],
        "city": dealership["city"],
        "state": dealership["state"],
        "form_detected": False,
        "complex_fields_detected": [],
        "fields_filled": [],
        "form_submitted": False,
        "submission_method": None,
        "submission_verification": None,
        "blocker": None,
        "error": None,
        "contact_url": None
    }

    playwright_instance = None
    browser = None

    try:
        # Create browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Use intelligent contact page finder
        finder = ContactPageFinder()
        contact_url = await finder.navigate_to_contact_page(page, dealership['website'])

        if not contact_url:
            result["error"] = "Could not find contact page"
            return result

        result["contact_url"] = contact_url
        await asyncio.sleep(3)

        # Detect form
        form_detector = EnhancedFormDetector()
        form_result = await form_detector.detect_contact_form(page)

        if not form_result.success:
            result["error"] = "No form detected"
            return result

        result["form_detected"] = True
        logger.info(f"✓ Form detected with {len(form_result.fields)} fields")

        # Initialize handlers
        complex_handler = ComplexFieldHandler()
        submitter = EnhancedFormSubmitter()

        # Detect complex fields
        split_phone = await complex_handler.detect_split_phone_field(page)
        if split_phone:
            result["complex_fields_detected"].append("split_phone")
            logger.info("✓ Split phone field detected")

        complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
        if complex_name:
            result["complex_fields_detected"].append("complex_name")
            logger.info("✓ Complex name field detected")

        gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)
        if gravity_zip:
            result["complex_fields_detected"].append("gravity_zip")
            logger.info("✓ Gravity Forms zip detected")

        # Fill complex fields
        if split_phone:
            success = await complex_handler.fill_split_phone_field(split_phone, TEST_DATA["phone"])
            if success:
                result["fields_filled"].append("phone_split")
                logger.info("✓ Filled split phone")

        if complex_name:
            success = await complex_handler.fill_complex_name_field(
                complex_name, TEST_DATA["first_name"], TEST_DATA["last_name"]
            )
            if success:
                result["fields_filled"].extend(["first_name", "last_name"])
                logger.info("✓ Filled complex name")

        if gravity_zip:
            await gravity_zip.fill(TEST_DATA["zip_code"])
            result["fields_filled"].append("zip_code")
            logger.info("✓ Filled gravity zip")

        # Fill standard fields
        logger.info("Filling standard fields...")
        for field_type, field_info in form_result.fields.items():
            # Skip if already handled
            if field_type == "phone" and split_phone:
                continue
            if field_type in ["first_name", "last_name"] and complex_name:
                continue
            if field_type in ["zip", "zip_code"] and gravity_zip:
                continue

            value = TEST_DATA.get(field_type)
            if not value:
                continue

            try:
                await field_info.element.fill(value)
                result["fields_filled"].append(field_type)
                logger.info(f"✓ Filled {field_type}")
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.warning(f"Failed to fill {field_type}: {str(e)}")

        # Take screenshot of filled form
        dealer_slug = dealership["dealer_name"].replace(" ", "_").replace("/", "_")[:50]
        screenshot_path = test_dir / "screenshots" / f"{dealer_slug}_filled.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Submit form with enhanced submitter
        logger.info("Attempting submission...")
        submission_result = await submitter.submit_form(page, form_result.form_element)

        result["form_submitted"] = submission_result.success
        result["submission_method"] = submission_result.method
        result["submission_verification"] = submission_result.verification
        result["blocker"] = submission_result.blocker

        if submission_result.success:
            logger.info(f"✅ FORM SUBMITTED SUCCESSFULLY!")
            logger.info(f"   Method: {submission_result.method}")
            logger.info(f"   Verified by: {submission_result.verification}")

            # Screenshot of success page
            success_screenshot = test_dir / "screenshots" / f"{dealer_slug}_success.png"
            await page.screenshot(path=str(success_screenshot), full_page=True)

        else:
            logger.warning(f"❌ Submission failed")
            logger.warning(f"   Blocker: {submission_result.blocker}")
            logger.warning(f"   Error: {submission_result.error}")

            # Track for manual follow-up if needed
            if submission_result.blocker == "CAPTCHA_DETECTED":
                captcha_tracker.add_site(
                    dealer_name=dealership["dealer_name"],
                    website=dealership["website"],
                    contact_url=result["contact_url"],
                    reason="CAPTCHA",
                    notes="Detected during automated submission"
                )
                logger.info("→ Added to manual follow-up tracker")

            # Screenshot of failed state
            fail_screenshot = test_dir / "screenshots" / f"{dealer_slug}_failed.png"
            await page.screenshot(path=str(fail_screenshot), full_page=True)

        await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        result["error"] = str(e)

    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass
        if playwright_instance:
            try:
                await playwright_instance.stop()
            except:
                pass

    return result


async def main():
    """Run comprehensive test on 20 new dealerships"""

    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE TEST WITH ALL IMPROVEMENTS")
    logger.info("Testing 20 new dealerships")
    logger.info("="*80 + "\n")

    # Create test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = Path(f"tests/comprehensive_test_{timestamp}")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Initialize CAPTCHA tracker
    captcha_tracker = CaptchaTracker()

    # Load dealerships
    dealerships = load_dealerships()
    logger.info(f"Loaded {len(dealerships)} dealerships from CSV")

    # Get previously tested sites to exclude
    previous_tests = [
        "houstondcjr.com", "shawanoauto.com", "fawsgaragecdjr.com",
        "lexingtonparkcdjr.com", "jbchryslerjeepdodgeram.com", "i10dodge.com",
        "rousemotor.com", "jimshorkeychryslerdodgejeepram.com", "macjeepram.com",
        "carsonchryslerdodge.com", "helfmandodge.net", "fillbackprairieduchiencdjr.com",
        "clementchryslerdodgejeepramflorissant.com", "lovechryslerdodgejeep.com",
        "caldwellchrysler.com", "davidstanleychryslerjeepdodgeofoklahoma.com",
        "mountainvalleymotors.net", "heritagechryslerjeepmaryland.com",
        "johnnyrobertsmotors.net", "keycdjrofrochester.com"
    ]

    # Select 20 new random dealerships
    test_dealerships = select_random_dealerships(dealerships, 20, previous_tests)
    logger.info(f"Selected {len(test_dealerships)} new dealerships for testing\n")

    # Test each dealership
    results = []
    for idx, dealership in enumerate(test_dealerships, 1):
        logger.info(f"\n[{idx}/20] Testing {dealership['dealer_name']}...")

        result = await test_dealership(dealership, test_dir, captcha_tracker)
        results.append(result)

        # Brief pause between tests
        await asyncio.sleep(3)

    # Save results
    results_file = test_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_dealerships": len(results),
            "results": results
        }, f, indent=2)

    # Generate CSV report
    csv_file = test_dir / "results.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'dealer_name', 'website', 'city', 'state', 'form_detected',
            'complex_fields_detected', 'fields_filled', 'form_submitted',
            'submission_method', 'submission_verification', 'blocker', 'error'
        ])
        writer.writeheader()

        for result in results:
            writer.writerow({
                **result,
                'complex_fields_detected': ', '.join(result['complex_fields_detected']),
                'fields_filled': ', '.join(result['fields_filled'])
            })

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*80 + "\n")

    total = len(results)
    detected = sum(1 for r in results if r['form_detected'])
    filled = sum(1 for r in results if len(r['fields_filled']) > 0)
    submitted = sum(1 for r in results if r['form_submitted'])
    captcha_blocked = sum(1 for r in results if r['blocker'] == 'CAPTCHA_DETECTED')

    logger.info(f"Total Tested: {total}")
    logger.info(f"Forms Detected: {detected}/{total} ({detected/total*100:.1f}%)")
    logger.info(f"Forms Filled: {filled}/{total} ({filled/total*100:.1f}%)")
    logger.info(f"Forms Submitted: {submitted}/{total} ({submitted/total*100:.1f}%)")
    logger.info(f"Blocked by CAPTCHA: {captcha_blocked}/{total} ({captcha_blocked/total*100:.1f}%)")

    # Complex fields summary
    split_phone_count = sum(1 for r in results if 'split_phone' in r['complex_fields_detected'])
    complex_name_count = sum(1 for r in results if 'complex_name' in r['complex_fields_detected'])
    gravity_zip_count = sum(1 for r in results if 'gravity_zip' in r['complex_fields_detected'])

    logger.info(f"\nComplex Fields Detected:")
    logger.info(f"  - Split Phone: {split_phone_count}")
    logger.info(f"  - Complex Name: {complex_name_count}")
    logger.info(f"  - Gravity Zip: {gravity_zip_count}")

    # Submission methods
    methods = {}
    for r in results:
        if r['submission_method']:
            methods[r['submission_method']] = methods.get(r['submission_method'], 0) + 1

    if methods:
        logger.info(f"\nSubmission Methods Used:")
        for method, count in methods.items():
            logger.info(f"  - {method}: {count}")

    logger.info(f"\nResults saved to: {test_dir}")
    logger.info(f"JSON: {results_file}")
    logger.info(f"CSV: {csv_file}")

    # Print CAPTCHA tracker summary
    captcha_tracker.print_summary()

    # Export pending sites
    if captcha_blocked > 0:
        export_path = captcha_tracker.export_pending_csv()
        logger.info(f"\nManual follow-up list exported to: {export_path}")

    logger.info("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
