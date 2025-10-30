"""
Early CAPTCHA Detection Utility

Detects CAPTCHA presence on pages BEFORE filling forms to save time.
Should be called immediately after page navigation, before any form interaction.
"""

from typing import Optional, Dict
from playwright.async_api import Page
from ...utils.logging import get_logger

logger = get_logger(__name__)


class EarlyCaptchaDetector:
    """Detect CAPTCHA presence early to avoid wasting time on forms we can't submit"""

    # Comprehensive CAPTCHA indicators
    CAPTCHA_SELECTORS = [
        # reCAPTCHA v2 (checkbox)
        ".g-recaptcha",
        "#g-recaptcha",
        "[data-sitekey]",
        "iframe[src*='recaptcha']",
        "iframe[title*='reCAPTCHA']",

        # reCAPTCHA v3 (invisible)
        ".grecaptcha-badge",
        "[data-callback*='recaptcha']",

        # hCaptcha
        ".h-captcha",
        "[data-hcaptcha-sitekey]",
        "iframe[src*='hcaptcha']",

        # Generic CAPTCHA indicators
        "iframe[src*='captcha']",
        "[class*='captcha']",
        "[id*='captcha']",
        ".captcha-container",
        "#captcha-container",

        # Cloudflare Turnstile
        ".cf-turnstile",
        "[data-turnstile-sitekey]",

        # Other common CAPTCHA services
        "[data-arkose]",  # Arkose Labs
        "[data-funcaptcha]",  # FunCaptcha
    ]

    def __init__(self):
        self.logger = logger

    async def detect_captcha(self, page: Page) -> Dict:
        """
        Detect CAPTCHA on page as early as possible.

        Returns:
            Dict with:
                - has_captcha: bool
                - captcha_type: Optional[str]
                - selector: Optional[str] - which selector matched
                - visible: bool - whether CAPTCHA is currently visible
        """

        self.logger.debug("Starting early CAPTCHA detection...")

        result = {
            "has_captcha": False,
            "captcha_type": None,
            "selector": None,
            "visible": False
        }

        # Check each selector
        for selector in self.CAPTCHA_SELECTORS:
            try:
                elements = page.locator(selector)
                count = await elements.count()

                if count > 0:
                    # Found a CAPTCHA indicator
                    self.logger.info(f"CAPTCHA detected: {selector} ({count} element(s) found)")

                    # Try to determine visibility
                    try:
                        first_element = elements.first
                        is_visible = await first_element.is_visible(timeout=1000)
                    except:
                        # If we can't check visibility, assume it's there
                        is_visible = True

                    # Determine CAPTCHA type from selector
                    captcha_type = self._determine_captcha_type(selector)

                    result = {
                        "has_captcha": True,
                        "captcha_type": captcha_type,
                        "selector": selector,
                        "visible": is_visible
                    }

                    self.logger.info(f"CAPTCHA type: {captcha_type}, visible: {is_visible}")
                    return result

            except Exception as e:
                self.logger.debug(f"Selector {selector} check failed: {str(e)}")
                continue

        # Additional check: Look for CAPTCHA in page content/scripts
        try:
            page_content = await page.content()
            content_lower = page_content.lower()

            # Check for CAPTCHA-related scripts/mentions
            captcha_keywords = [
                'recaptcha/api.js',
                'recaptcha/releases',
                'hcaptcha.com',
                'challenges.cloudflare.com',
                'funcaptcha.com'
            ]

            for keyword in captcha_keywords:
                if keyword in content_lower:
                    self.logger.info(f"CAPTCHA detected in page content: {keyword}")
                    result = {
                        "has_captcha": True,
                        "captcha_type": self._keyword_to_type(keyword),
                        "selector": "page_content",
                        "visible": True  # Assume visible if loaded
                    }
                    return result

        except Exception as e:
            self.logger.debug(f"Content check failed: {str(e)}")

        self.logger.debug("No CAPTCHA detected")
        return result

    def _determine_captcha_type(self, selector: str) -> str:
        """Determine CAPTCHA type from selector"""
        selector_lower = selector.lower()

        if 'recaptcha' in selector_lower or 'grecaptcha' in selector_lower:
            return "reCAPTCHA"
        elif 'hcaptcha' in selector_lower:
            return "hCaptcha"
        elif 'turnstile' in selector_lower or 'cloudflare' in selector_lower:
            return "Cloudflare Turnstile"
        elif 'arkose' in selector_lower or 'funcaptcha' in selector_lower:
            return "FunCaptcha"
        else:
            return "Unknown CAPTCHA"

    def _keyword_to_type(self, keyword: str) -> str:
        """Convert keyword to CAPTCHA type"""
        keyword_lower = keyword.lower()

        if 'recaptcha' in keyword_lower:
            return "reCAPTCHA"
        elif 'hcaptcha' in keyword_lower:
            return "hCaptcha"
        elif 'cloudflare' in keyword_lower or 'turnstile' in keyword_lower:
            return "Cloudflare Turnstile"
        elif 'funcaptcha' in keyword_lower or 'arkose' in keyword_lower:
            return "FunCaptcha"
        else:
            return "Unknown CAPTCHA"

    async def wait_and_detect(
        self,
        page: Page,
        wait_seconds: float = 2.0,
        max_wait_seconds: float = 5.0,
        check_interval: float = 0.5
    ) -> Dict:
        """
        Wait for page to stabilize with progressive CAPTCHA detection.

        Checks every check_interval seconds up to max_wait_seconds.
        Returns immediately if CAPTCHA detected, or after max_wait if none found.

        Args:
            page: Playwright page
            wait_seconds: Minimum seconds to wait before returning (default 2.0)
            max_wait_seconds: Maximum seconds to wait (default 5.0)
            check_interval: How often to check for CAPTCHA (default 0.5s)

        Returns:
            Detection result dict
        """
        import asyncio

        self.logger.debug(f"Progressive CAPTCHA detection: checking every {check_interval}s, up to {max_wait_seconds}s...")
        elapsed = 0.0
        result = {"has_captcha": False, "captcha_type": None, "selector": None, "visible": False}

        while elapsed < max_wait_seconds:
            await asyncio.sleep(check_interval)
            elapsed += check_interval

            # Check for CAPTCHA at each interval
            result = await self.detect_captcha(page)

            if result["has_captcha"]:
                self.logger.info(f"CAPTCHA detected after {elapsed:.1f}s")
                return result  # Return immediately when found

            # Continue checking until we hit minimum wait time
            if elapsed >= wait_seconds and not result["has_captcha"]:
                # No CAPTCHA after minimum wait, safe to proceed
                break

        # No CAPTCHA found after thorough check
        self.logger.debug(f"No CAPTCHA detected after {elapsed:.1f}s")
        return result
