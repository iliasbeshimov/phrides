"""
Comprehensive test with INTELLIGENT CONTACT DISCOVERY:
1. Contact URL caching (10x faster on repeat visits)
2. Multi-attempt strategy (try multiple URLs if first has weak form)
3. Form validation (ensure good forms before accepting)
4. Complex field detection (split phone, gravity forms)
5. Enhanced submission with verification
6. CAPTCHA tracking for manual follow-up

TRACKING & REPORTING:
- Contact forms identified
- Contact forms filled in fully
- Honeypot fields detected and skipped
- Forms submitted successfully
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
from src.automation.forms.early_captcha_detector import EarlyCaptchaDetector
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.services.captcha_tracker import CaptchaTracker
from src.services.contact_url_cache import ContactURLCache
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


async def validate_contact_form(page):
    """
    Validate that page has a good contact form.

    Returns:
        (success: bool, form_data: dict or None)
    """
    logger.debug("=== VALIDATOR CALLED ===")
    detector = EnhancedFormDetector()
    result = await detector.detect_contact_form(page)

    logger.debug(f"Form detection result: success={result.success}, field_count={len(result.fields) if result.fields else 0}")

    if not result.success:
        logger.debug("Form detection failed - returning (False, None)")
        return (False, None)

    # Good form needs at least 4 fields (name, email, phone, message)
    field_count = len(result.fields)
    if field_count < 4:
        logger.debug(f"Weak form detected: only {field_count} fields - returning (False, None)")
        return (False, None)

    form_data = {
        'field_count': field_count,
        'field_types': list(result.fields.keys()),
        'has_submit': bool(result.submit_button),
        'form_type': 'standard',  # Could detect specific types
        'confidence': result.confidence_score
    }

    logger.debug(f"Form validated successfully! Returning (True, {form_data})")
    return (True, form_data)


async def test_dealership(dealership: Dict, test_dir: Path, captcha_tracker: CaptchaTracker,
                         contact_finder: ContactPageFinder) -> Dict:
    """Test single dealership with intelligent discovery and comprehensive tracking"""

    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {dealership['dealer_name']}")
    logger.info(f"Website: {dealership['website']}")
    logger.info(f"{'='*80}\n")

    result = {
        "dealer_name": dealership["dealer_name"],
        "website": dealership["website"],
        "city": dealership["city"],
        "state": dealership["state"],

        # Contact page discovery
        "contact_url_found": False,
        "contact_url": None,
        "contact_url_source": None,  # "cache", "homepage_link", "pattern"
        "urls_tried": 0,

        # Form detection
        "form_detected": False,
        "form_field_count": 0,
        "form_confidence": 0.0,

        # Complex fields
        "complex_fields_detected": [],

        # Form filling
        "fields_filled": [],
        "fields_skipped": [],
        "honeypot_fields_detected": 0,
        "fill_success": False,

        # Submission
        "form_submitted": False,
        "submission_method": None,
        "submission_verification": None,
        "blocker": None,

        # Errors
        "error": None
    }

    playwright_instance = None
    browser = None

    try:
        # Create browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Use intelligent contact page finder with form validation
        logger.info("Finding contact page with intelligent discovery...")
        contact_url, form_data = await contact_finder.navigate_to_contact_page(
            page=page,
            website_url=dealership['website'],
            form_validator=validate_contact_form
        )

        if not contact_url:
            result["error"] = "No contact page with valid form found"
            return result

        result["contact_url_found"] = True
        result["contact_url"] = contact_url
        result["form_detected"] = True
        result["form_field_count"] = form_data.get('field_count', 0)
        result["form_confidence"] = form_data.get('confidence', 0.0)

        logger.info(f"✅ Contact page: {contact_url}")
        logger.info(f"✅ Form detected with {form_data['field_count']} fields (confidence: {form_data['confidence']})")

        await asyncio.sleep(3)

        # EARLY CAPTCHA DETECTION - Check BEFORE filling any fields
        logger.info("🔍 Checking for CAPTCHA before filling form...")
        captcha_detector = EarlyCaptchaDetector()
        captcha_result = await captcha_detector.wait_and_detect(page, wait_seconds=2.0)

        if captcha_result["has_captcha"]:
            logger.warning(f"⚠️  CAPTCHA DETECTED EARLY: {captcha_result['captcha_type']}")
            logger.warning(f"   Selector: {captcha_result['selector']}")
            logger.warning(f"   Visible: {captcha_result['visible']}")
            logger.warning("   Skipping form filling to save time...")

            result["form_detected"] = True  # We found the form
            result["blocker"] = "CAPTCHA_DETECTED"
            result["error"] = f"{captcha_result['captcha_type']} detected on page"

            # Track for manual follow-up
            captcha_tracker.add_site(
                dealer_name=dealership["dealer_name"],
                website=dealership["website"],
                contact_url=result["contact_url"],
                reason="CAPTCHA",
                captcha_type=captcha_result["captcha_type"],
                notes=f"Early detection: {captcha_result['selector']}"
            )

            # Take screenshot showing CAPTCHA
            dealer_slug = dealership["dealer_name"].replace(" ", "_").replace("/", "_")[:50]
            screenshot_path = test_dir / "screenshots" / f"{dealer_slug}_captcha_detected.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)

            logger.info("→ Added to manual follow-up tracker (early detection)")
            return result

        logger.info("✅ No CAPTCHA detected - proceeding with form filling")

        # Re-detect form for detailed field information
        form_detector = EnhancedFormDetector()
        form_result = await form_detector.detect_contact_form(page)

        if not form_result.success:
            result["error"] = "Form detection failed on re-check"
            return result

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
            # Skip if already handled by complex handlers
            if field_type == "phone" and split_phone:
                result["fields_skipped"].append(f"{field_type}_complex")
                continue
            if field_type in ["first_name", "last_name"] and complex_name:
                result["fields_skipped"].append(f"{field_type}_complex")
                continue
            if field_type in ["zip", "zip_code"] and gravity_zip:
                result["fields_skipped"].append(f"{field_type}_complex")
                continue

            # Detect honeypot fields (common patterns)
            field_name = await field_info.element.get_attribute("name") or ""
            field_id = await field_info.element.get_attribute("id") or ""

            honeypot_indicators = ['honeypot', 'hp_', 'bot', 'trap', 'hidden_field']
            is_honeypot = any(indicator in field_name.lower() or indicator in field_id.lower()
                            for indicator in honeypot_indicators)

            if is_honeypot:
                result["honeypot_fields_detected"] += 1
                result["fields_skipped"].append(f"{field_type}_honeypot")
                logger.info(f"⚠️  Skipped honeypot field: {field_type}")
                continue

            value = TEST_DATA.get(field_type)
            if not value:
                result["fields_skipped"].append(f"{field_type}_no_data")
                continue

            try:
                await field_info.element.fill(value)
                result["fields_filled"].append(field_type)
                logger.info(f"✓ Filled {field_type}")
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.warning(f"Failed to fill {field_type}: {str(e)}")
                result["fields_skipped"].append(f"{field_type}_error")

        # Mark fill as successful if we filled at least 4 fields
        result["fill_success"] = len(result["fields_filled"]) >= 4

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
    """Run comprehensive test on 20 dealerships with intelligent discovery"""

    logger.info("\n" + "="*80)
    logger.info("COMPREHENSIVE TEST WITH INTELLIGENT CONTACT DISCOVERY")
    logger.info("Testing 20 dealerships")
    logger.info("="*80 + "\n")

    # Create test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = Path(f"tests/intelligent_discovery_test_{timestamp}")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Initialize trackers
    captcha_tracker = CaptchaTracker()
    contact_finder = ContactPageFinder(use_cache=True)
    url_cache = ContactURLCache()

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
        "johnnyrobertsmotors.net", "keycdjrofrochester.com",
        "foxhillschryslerjeepplymouth.com", "deyarmancdjr.com", "friendlycdjrhamilton.com",
        "stoneridgechryslerjeepdodgeofdublin.com", "cannoncdjrofcleveland.com",
        "fremontchryslerdodgejeepcasper.com", "navarrecdjr.com", "miraclechrysler.com",
        "huffineschryslerjeepdodgeramplano.com", "clintonchryslerdodgejeep.com",
        "diehlcdjrofmoon.com", "kingchryslerdodge.net", "directautocdjr.com",
        "ronlewisjeep.com", "williamschryslerdodgejeep.com", "kellyjeep.com",
        "earnhardtqueencreek.com", "garavelcdjr.com", "jayhodgedodge.com", "poguecdjr.com"
    ]

    # Select 20 new random dealerships
    test_dealerships = select_random_dealerships(dealerships, 20, previous_tests)
    logger.info(f"Selected {len(test_dealerships)} new dealerships for testing\n")

    # Test each dealership
    results = []
    for idx, dealership in enumerate(test_dealerships, 1):
        logger.info(f"\n[{idx}/20] Testing {dealership['dealer_name']}...")

        result = await test_dealership(dealership, test_dir, captcha_tracker, contact_finder)
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
            'dealer_name', 'website', 'city', 'state',
            'contact_url_found', 'contact_url', 'form_detected', 'form_field_count',
            'complex_fields_detected', 'fields_filled', 'fields_skipped',
            'honeypot_fields_detected', 'fill_success',
            'form_submitted', 'submission_method', 'submission_verification',
            'blocker', 'error'
        ])
        writer.writeheader()

        for result in results:
            writer.writerow({
                **result,
                'complex_fields_detected': ', '.join(result['complex_fields_detected']),
                'fields_filled': ', '.join(result['fields_filled']),
                'fields_skipped': ', '.join(result['fields_skipped'])
            })

    # Print comprehensive summary
    logger.info("\n" + "="*80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*80 + "\n")

    total = len(results)

    # Contact page discovery
    contact_found = sum(1 for r in results if r['contact_url_found'])

    # Form detection
    forms_detected = sum(1 for r in results if r['form_detected'])

    # Form filling
    forms_filled_fully = sum(1 for r in results if r['fill_success'])
    total_fields_filled = sum(len(r['fields_filled']) for r in results)
    total_fields_skipped = sum(len(r['fields_skipped']) for r in results)
    total_honeypots = sum(r['honeypot_fields_detected'] for r in results)

    # Form submission
    forms_submitted = sum(1 for r in results if r['form_submitted'])
    captcha_blocked = sum(1 for r in results if r['blocker'] == 'CAPTCHA_DETECTED')

    logger.info(f"📊 CONTACT PAGE DISCOVERY:")
    logger.info(f"   Total Tested: {total}")
    logger.info(f"   Contact Pages Found: {contact_found}/{total} ({contact_found/total*100:.1f}%)")
    logger.info(f"")

    logger.info(f"📝 FORM DETECTION:")
    logger.info(f"   Forms Detected: {forms_detected}/{total} ({forms_detected/total*100:.1f}%)")
    avg_fields = sum(r['form_field_count'] for r in results) / max(forms_detected, 1)
    logger.info(f"   Average Fields per Form: {avg_fields:.1f}")
    logger.info(f"")

    logger.info(f"✏️  FORM FILLING:")
    logger.info(f"   Forms Filled Fully: {forms_filled_fully}/{total} ({forms_filled_fully/total*100:.1f}%)")
    logger.info(f"   Total Fields Filled: {total_fields_filled}")
    logger.info(f"   Total Fields Skipped: {total_fields_skipped}")
    logger.info(f"   Honeypot Fields Detected & Skipped: {total_honeypots}")
    logger.info(f"")

    logger.info(f"🚀 FORM SUBMISSION:")
    logger.info(f"   Forms Submitted Successfully: {forms_submitted}/{total} ({forms_submitted/total*100:.1f}%)")
    logger.info(f"   Blocked by CAPTCHA: {captcha_blocked}/{total} ({captcha_blocked/total*100:.1f}%)")

    # Calculate submission rate excluding CAPTCHA sites
    non_captcha = total - captcha_blocked
    if non_captcha > 0:
        non_captcha_success_rate = (forms_submitted / non_captcha) * 100
        logger.info(f"   Success Rate (excluding CAPTCHA): {forms_submitted}/{non_captcha} ({non_captcha_success_rate:.1f}%)")
    logger.info(f"")

    # Complex fields summary
    split_phone_count = sum(1 for r in results if 'split_phone' in r['complex_fields_detected'])
    complex_name_count = sum(1 for r in results if 'complex_name' in r['complex_fields_detected'])
    gravity_zip_count = sum(1 for r in results if 'gravity_zip' in r['complex_fields_detected'])

    logger.info(f"🔧 COMPLEX FIELDS HANDLED:")
    logger.info(f"   Split Phone: {split_phone_count}")
    logger.info(f"   Complex Name: {complex_name_count}")
    logger.info(f"   Gravity Zip: {gravity_zip_count}")
    logger.info(f"")

    # Submission methods
    methods = {}
    for r in results:
        if r['submission_method']:
            methods[r['submission_method']] = methods.get(r['submission_method'], 0) + 1

    if methods:
        logger.info(f"📤 SUBMISSION METHODS USED:")
        for method, count in methods.items():
            logger.info(f"   {method}: {count}")
        logger.info(f"")

    logger.info(f"💾 Results saved to: {test_dir}")
    logger.info(f"   JSON: {results_file}")
    logger.info(f"   CSV: {csv_file}")
    logger.info(f"")

    # Print cache statistics
    url_cache.print_summary()

    # Print CAPTCHA tracker summary
    captcha_tracker.print_summary()

    # Export pending sites
    if captcha_blocked > 0:
        export_path = captcha_tracker.export_pending_csv()
        logger.info(f"📋 Manual follow-up list exported to: {export_path}")

    logger.info("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
