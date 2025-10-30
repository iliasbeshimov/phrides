"""
Test the improved contact page finder on ASP.NET sites that use /contactus.aspx
"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.utils.logging import get_logger

logger = get_logger(__name__)


TEST_SITES = [
    {
        "name": "Fremont Motor Casper",
        "website": "https://www.fremontchryslerdodgejeepcasper.com",
        "expected_contact": "/contactus.aspx"
    },
    {
        "name": "Huffines CJDR Plano",
        "website": "https://www.huffineschryslerjeepdodgeramplano.com",
        "expected_contact": "/contact.htm"
    }
]


async def test_site(site_info: dict):
    """Test contact page finder on a single site"""

    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {site_info['name']}")
    logger.info(f"Website: {site_info['website']}")
    logger.info(f"{'='*80}\n")

    playwright_instance = None
    browser = None

    try:
        # Create browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Test contact page finder
        finder = ContactPageFinder()
        contact_url = await finder.navigate_to_contact_page(page, site_info['website'])

        if contact_url:
            logger.info(f"✅ Contact page found: {contact_url}")

            # Check if it matches expected
            if site_info['expected_contact'] in contact_url:
                logger.info(f"✅ Matches expected pattern: {site_info['expected_contact']}")
            else:
                logger.warning(f"⚠️  Different pattern than expected")
                logger.warning(f"   Expected: {site_info['expected_contact']}")
                logger.warning(f"   Found: {contact_url}")

            # Try to detect form
            await asyncio.sleep(3)
            form_detector = EnhancedFormDetector()
            form_result = await form_detector.detect_contact_form(page)

            if form_result.success:
                logger.info(f"✅ Form detected with {len(form_result.fields)} fields")
                logger.info(f"   Fields: {list(form_result.fields.keys())}")
            else:
                logger.warning(f"❌ Form detection failed")

            # Take screenshot
            await page.screenshot(path=f"test_contact_finder_{site_info['name'].replace(' ', '_')}.png", full_page=True)

        else:
            logger.error(f"❌ Contact page NOT found")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

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


async def main():
    """Test both sites"""

    logger.info("\n" + "="*80)
    logger.info("TESTING CONTACT PAGE FINDER ON ASP.NET SITES")
    logger.info("="*80 + "\n")

    for site in TEST_SITES:
        await test_site(site)
        await asyncio.sleep(2)

    logger.info("\n" + "="*80)
    logger.info("TEST COMPLETE")
    logger.info("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
