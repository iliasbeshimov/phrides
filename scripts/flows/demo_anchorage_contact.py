"""Demonstrate the Anchorage Chrysler Center modal contact flow."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[2]
import sys
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager


CONTACT_URL = "https://www.anchoragechryslercenter.com/contactus"
SCREENSHOT_PATH = Path("tests/fixtures/form_detection/screenshots/anchorage_chrysler_center_form.png")


async def main() -> None:
    manager = EnhancedStealthBrowserManager()

    async with async_playwright() as pw:
        browser, context = await manager.open_context(pw, headless=False)
        page = await manager.create_enhanced_stealth_page(context)

        try:
            await page.goto(CONTACT_URL, wait_until="domcontentloaded", timeout=60000)
        except PlaywrightTimeoutError:
            print("Initial navigation timed out; aborting")
            await page.close()
            await manager.close_context(browser, context)
            return

        # Mimic a human pause on load
        await page.wait_for_timeout(1200)

        # Dismiss cookie banner if present
        try:
            await page.locator("button:has-text(\"Ok\")").first.click(timeout=2000)
            await page.wait_for_timeout(500)
        except Exception:
            pass

        # Scroll to bring the CTA into view slowly
        await page.evaluate("window.scrollBy({top: 350, behavior: 'smooth'})")
        await page.wait_for_timeout(1200)

        cta = page.locator("a:has-text('Send Us A Message')").first
        await cta.hover()
        await page.wait_for_timeout(600)
        await cta.click()
        await page.wait_for_timeout(800)

        # Select the 'Sales' option in the modal
        sales_button = page.locator("#textmodal___BV_modal_body_ a:has-text('Sales')")
        await sales_button.hover()
        await page.wait_for_timeout(400)
        await sales_button.click()

        # Wait for the lead form to appear
        form = page.locator("form.contactForm")
        await form.wait_for(timeout=10000)
        await page.wait_for_timeout(800)

        # Capture a screenshot of the form state
        SCREENSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(SCREENSHOT_PATH), full_page=False)

        # Log detected form fields for reference
        selectors = {
            "first_name": "#firstName",
            "last_name": "#lastName",
            "preferred_contact": ".preferred-contact .custom-select-dropdown",
            "email": "#emailAddress",
            "phone": "#phoneNumber",
            "zip": "#zipCode",
            "message": "#textarea",
            "tcpa_checkbox": "input[id='23marketing-text-disclaimer']",
            "submit": "input[type='submit'][value='Send']",
        }

        print("Anchorage Chrysler Center form selectors:")
        for name, selector in selectors.items():
            count = await page.locator(selector).count()
            print(f"  {name:20s} -> {selector} ({'found' if count else 'missing'})")

        await page.close()
        await manager.close_context(browser, context)


if __name__ == "__main__":
    asyncio.run(main())
