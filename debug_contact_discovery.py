"""
Debug script to test contact page discovery with ONE dealership
"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def validate_contact_form(page):
    """Validate that page has a good contact form"""
    logger.info("=== VALIDATOR CALLED ===")
    detector = EnhancedFormDetector()
    result = await detector.detect_contact_form(page)

    logger.info(f"Form detection result: success={result.success}, field_count={len(result.fields) if result.fields else 0}")

    if result.success and result.fields:
        logger.info(f"Detected fields: {list(result.fields.keys())}")

    if not result.success:
        logger.info("Form detection failed - returning (False, None)")
        return (False, None)

    # Good form needs at least 4 fields
    field_count = len(result.fields)
    if field_count < 4:
        logger.info(f"Weak form detected: only {field_count} fields - returning (False, None)")
        return (False, None)

    form_data = {
        'field_count': field_count,
        'field_types': list(result.fields.keys()),
        'has_submit': bool(result.submit_button),
        'form_type': 'standard',
        'confidence': result.confidence_score
    }

    logger.info(f"✅ Form validated successfully! Returning (True, {form_data})")
    return (True, form_data)


async def main():
    # Test with a known good dealership
    test_site = "https://www.pilsonchryslerdodgejeep.com"

    logger.info(f"Testing contact discovery on: {test_site}")
    logger.info("="*80)

    playwright_instance = None
    browser = None

    try:
        # Create browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Create contact finder
        contact_finder = ContactPageFinder(use_cache=True)

        # Try to find contact page
        logger.info("\n🔍 Starting intelligent contact discovery...")
        contact_url, form_data = await contact_finder.navigate_to_contact_page(
            page=page,
            website_url=test_site,
            form_validator=validate_contact_form
        )

        logger.info("\n" + "="*80)
        logger.info("RESULT:")
        logger.info(f"  Contact URL: {contact_url}")
        logger.info(f"  Form Data: {form_data}")
        logger.info("="*80)

        if contact_url:
            logger.info(f"\n✅ SUCCESS! Found contact page at: {contact_url}")
            logger.info(f"   Form has {form_data.get('field_count', 0)} fields")
            logger.info(f"   Field types: {form_data.get('field_types', [])}")
        else:
            logger.error("\n❌ FAILED to find contact page with valid form")

        # Keep browser open for inspection
        await asyncio.sleep(10)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

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


if __name__ == "__main__":
    asyncio.run(main())
