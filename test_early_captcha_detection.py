"""
Quick test of early CAPTCHA detection on known CAPTCHA sites from Oct 20 test.

Tests the new EarlyCaptchaDetector to ensure it catches CAPTCHA before form filling.
"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.early_captcha_detector import EarlyCaptchaDetector
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Known CAPTCHA sites from Oct 20, 2025 test
CAPTCHA_SITES = [
    {
        "name": "Jimmy Britt Chrysler Jeep Dodge Ram",
        "url": "https://www.jbchryslerjeepdodgeram.com/contact.htm",
        "state": "GA"
    },
    {
        "name": "Porterville Chrysler Jeep Dodge",
        "url": "https://www.portervillecjd.com/contact.htm",
        "state": "CA"
    },
    {
        "name": "McClane Motor Sales Inc",
        "url": "https://www.mcclanemotor.com/contact.htm",
        "state": "IL"
    },
    {
        "name": "Herpolsheimer's",
        "url": "https://www.herpolsheimers.net/contact.htm",
        "state": "NE"
    }
]


async def test_single_site(site_info: dict) -> dict:
    """Test CAPTCHA detection on a single site"""

    logger.info(f"\n{'='*80}")
    logger.info(f"Testing: {site_info['name']} ({site_info['state']})")
    logger.info(f"URL: {site_info['url']}")
    logger.info(f"{'='*80}\n")

    result = {
        "name": site_info["name"],
        "url": site_info["url"],
        "captcha_detected": False,
        "captcha_type": None,
        "detection_time": None,
        "error": None
    }

    playwright_instance = None
    browser = None

    try:
        # Create browser
        playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

        # Navigate to contact page
        logger.info(f"Navigating to {site_info['url']}...")
        import time
        start_time = time.time()

        await page.goto(site_info['url'], wait_until='domcontentloaded', timeout=30000)

        # Wait for page to stabilize
        await asyncio.sleep(2)

        # Run early CAPTCHA detection
        logger.info("Running early CAPTCHA detection...")
        detector = EarlyCaptchaDetector()
        captcha_result = await detector.detect_captcha(page)

        detection_time = time.time() - start_time

        if captcha_result["has_captcha"]:
            logger.info(f"✅ CAPTCHA DETECTED!")
            logger.info(f"   Type: {captcha_result['captcha_type']}")
            logger.info(f"   Selector: {captcha_result['selector']}")
            logger.info(f"   Visible: {captcha_result['visible']}")
            logger.info(f"   Detection time: {detection_time:.2f}s")

            result["captcha_detected"] = True
            result["captcha_type"] = captcha_result["captcha_type"]
            result["detection_time"] = detection_time
        else:
            logger.warning(f"❌ CAPTCHA NOT DETECTED (expected to find one)")
            result["detection_time"] = detection_time

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
    """Test early CAPTCHA detection on known CAPTCHA sites"""

    logger.info("\n" + "="*80)
    logger.info("EARLY CAPTCHA DETECTION TEST")
    logger.info(f"Testing {len(CAPTCHA_SITES)} known CAPTCHA sites")
    logger.info("="*80 + "\n")

    results = []

    for site_info in CAPTCHA_SITES:
        result = await test_single_site(site_info)
        results.append(result)

        # Small delay between tests
        await asyncio.sleep(3)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)

    detected = sum(1 for r in results if r["captcha_detected"])
    total = len(results)

    logger.info(f"\nCAPTCHA Detection Rate: {detected}/{total} ({detected/total*100:.1f}%)")

    for result in results:
        status = "✅ DETECTED" if result["captcha_detected"] else "❌ MISSED"
        captcha_type = result["captcha_type"] or "N/A"
        time_str = f"{result['detection_time']:.2f}s" if result["detection_time"] else "N/A"

        logger.info(f"\n{result['name']}:")
        logger.info(f"  Status: {status}")
        logger.info(f"  Type: {captcha_type}")
        logger.info(f"  Time: {time_str}")
        if result["error"]:
            logger.info(f"  Error: {result['error']}")

    if detected == total:
        logger.info(f"\n🎉 SUCCESS! All {total} CAPTCHA sites detected correctly!")
    else:
        logger.info(f"\n⚠️  {total - detected} CAPTCHA sites were missed")

    logger.info("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
