"""Test discovery fix on a failed site"""
import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.utils.logging import get_logger

logger = get_logger(__name__)

async def validate_contact_form(page):
    detector = EnhancedFormDetector()
    result = await detector.detect_contact_form(page)

    if not result.success or len(result.fields) < 4:
        return (False, None)

    return (True, {
        'field_count': len(result.fields),
        'field_types': list(result.fields.keys()),
        'has_submit': bool(result.submit_button),
        'confidence': result.confidence_score
    })

async def main():
    # Test a site that failed: Chris Nikel (homepage fails to load)
    test_site = "https://www.chrisnikel.com"

    logger.info(f"Testing: {test_site}")

    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

    try:
        contact_finder = ContactPageFinder(use_cache=False)

        contact_url, form_data = await contact_finder.navigate_to_contact_page(
            page=page,
            website_url=test_site,
            form_validator=validate_contact_form
        )

        logger.info(f"\nResult:")
        logger.info(f"  Contact URL: {contact_url}")
        logger.info(f"  Form Data: {form_data}")

        if contact_url:
            logger.info(f"\n✅ SUCCESS!")
        else:
            logger.error(f"\n❌ FAILED")

        await asyncio.sleep(5)

    finally:
        if browser:
            await browser.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())
