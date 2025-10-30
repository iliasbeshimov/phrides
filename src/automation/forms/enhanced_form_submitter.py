"""
Enhanced form submitter with improved success rate for submissions.
Handles validation, consent checkboxes, CAPTCHAs, and submission verification.
"""

import asyncio
import re
from typing import Optional, Dict, List, Tuple
from playwright.async_api import Page, Locator
from dataclasses import dataclass

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SubmissionResult:
    """Result of form submission attempt"""
    success: bool
    method: str  # How submission was attempted
    blocker: Optional[str]  # What prevented submission if failed
    verification: Optional[str]  # How success was verified
    error: Optional[str]


class EnhancedFormSubmitter:
    """Enhanced form submitter with higher success rate"""

    def __init__(self):
        self.logger = logger

    async def submit_form(self, page: Page, form_container: Optional[Locator] = None) -> SubmissionResult:
        """
        Submit form with comprehensive strategies and verification.

        Strategies:
        1. Check for required fields and consent checkboxes
        2. Validate fields before submission
        3. Find and click submit button with multiple methods
        4. Verify submission success
        5. Handle common blockers (CAPTCHA, overlays)
        """

        self.logger.info("Starting enhanced form submission", {"operation": "form_submission_start"})

        try:
            # Step 1: Check for and handle consent checkboxes
            await self._handle_consent_checkboxes(page)

            # Step 2: Check for CAPTCHA (blocker detection)
            has_captcha = await self._detect_captcha(page)
            if has_captcha:
                self.logger.warning("CAPTCHA detected - cannot submit automatically")
                return SubmissionResult(
                    success=False,
                    method="none",
                    blocker="CAPTCHA_DETECTED",
                    verification=None,
                    error="Form has CAPTCHA challenge"
                )

            # Step 3: Validate fields
            validation_issues = await self._check_validation_errors(page)
            if validation_issues:
                self.logger.warning(f"Validation issues found: {validation_issues}")

            # Step 4: Find submit button
            submit_button = await self._find_submit_button_comprehensive(page, form_container)

            if not submit_button:
                self.logger.error("No submit button found")
                return SubmissionResult(
                    success=False,
                    method="none",
                    blocker="NO_SUBMIT_BUTTON",
                    verification=None,
                    error="Could not find submit button"
                )

            # Step 5: Attempt submission
            submission_method, clicked = await self._attempt_submission(page, submit_button)

            if not clicked:
                return SubmissionResult(
                    success=False,
                    method=submission_method,
                    blocker="CLICK_FAILED",
                    verification=None,
                    error="Failed to click submit button"
                )

            # Step 6: Wait and verify submission
            await asyncio.sleep(2)  # Wait for submission to process

            verification = await self._verify_submission_success(page)

            success = verification['success']

            self.logger.info(f"Form submission completed: {success}", {
                "operation": "form_submission_complete",
                "success": success,
                "method": submission_method,
                "verification": verification['method']
            })

            return SubmissionResult(
                success=success,
                method=submission_method,
                blocker=None if success else "SUBMISSION_FAILED",
                verification=verification['method'],
                error=None if success else verification.get('reason')
            )

        except Exception as e:
            self.logger.error(f"Form submission exception: {str(e)}")
            return SubmissionResult(
                success=False,
                method="exception",
                blocker="EXCEPTION",
                verification=None,
                error=str(e)
            )

    async def _handle_consent_checkboxes(self, page: Page) -> None:
        """Find and check consent/agreement checkboxes"""

        # Common consent checkbox patterns
        consent_patterns = [
            "input[type='checkbox'][name*='consent' i]",
            "input[type='checkbox'][name*='agree' i]",
            "input[type='checkbox'][name*='privacy' i]",
            "input[type='checkbox'][name*='terms' i]",
            "input[type='checkbox'][id*='consent' i]",
            "input[type='checkbox'][id*='agree' i]",
            ".consent input[type='checkbox']",
            ".agreement input[type='checkbox']"
        ]

        for pattern in consent_patterns:
            try:
                checkboxes = page.locator(pattern)
                count = await checkboxes.count()

                for i in range(count):
                    checkbox = checkboxes.nth(i)

                    # Check if visible and not already checked
                    if await checkbox.is_visible() and not await checkbox.is_checked():
                        await checkbox.check()
                        self.logger.info(f"Checked consent checkbox: {pattern}")
                        await asyncio.sleep(0.3)

            except Exception as e:
                self.logger.debug(f"Consent checkbox pattern {pattern} failed: {str(e)}")
                continue

    async def _detect_captcha(self, page: Page) -> bool:
        """Detect if form has CAPTCHA"""

        captcha_indicators = [
            ".g-recaptcha",
            "#recaptcha",
            "[data-sitekey]",
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            ".h-captcha",
            "[data-hcaptcha]"
        ]

        for indicator in captcha_indicators:
            try:
                elements = page.locator(indicator)
                if await elements.count() > 0:
                    self.logger.info(f"CAPTCHA detected: {indicator}")
                    return True
            except:
                continue

        return False

    async def _check_validation_errors(self, page: Page) -> List[str]:
        """Check for client-side validation errors"""

        errors = []

        try:
            # Check for visible error messages
            error_selectors = [
                ".error:visible",
                ".error-message:visible",
                ".field-error:visible",
                "[aria-invalid='true']",
                "input:invalid"
            ]

            for selector in error_selectors:
                elements = page.locator(selector)
                count = await elements.count()

                if count > 0:
                    for i in range(min(count, 5)):  # Check first 5
                        try:
                            text = await elements.nth(i).text_content()
                            if text and text.strip():
                                errors.append(text.strip())
                        except:
                            pass

        except Exception as e:
            self.logger.debug(f"Validation check error: {str(e)}")

        return errors

    async def _find_submit_button_comprehensive(self, page: Page, form_container: Optional[Locator]) -> Optional[Locator]:
        """Find submit button using comprehensive strategies"""

        container = form_container or page

        # Strategy 1: Standard submit button selectors
        standard_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send')",
            "button:has-text('Send Message')",
            "button:has-text('Contact Us')",
            "button:has-text('Get Quote')",
            "button:has-text('Request Info')",
            "input[value*='Submit' i]",
            ".submit-btn",
            ".btn-submit",
            "#submit",
            "[data-action='submit']"
        ]

        for selector in standard_selectors:
            try:
                buttons = container.locator(selector)
                count = await buttons.count()

                for i in range(count):
                    button = buttons.nth(i)
                    if await button.is_visible() and await button.is_enabled():
                        self.logger.info(f"Found submit button: {selector}")
                        return button
            except:
                continue

        # Strategy 2: Look for buttons with submit-like text
        try:
            buttons = container.locator("button")
            count = await buttons.count()

            for i in range(count):
                button = buttons.nth(i)
                try:
                    text = (await button.text_content() or "").lower().strip()
                    if any(word in text for word in ['submit', 'send', 'contact', 'request', 'get']):
                        if await button.is_visible() and await button.is_enabled():
                            self.logger.info(f"Found submit button by text: '{text}'")
                            return button
                except:
                    continue
        except:
            pass

        return None

    async def _attempt_submission(self, page: Page, submit_button: Locator) -> Tuple[str, bool]:
        """Attempt to submit form with multiple methods"""

        # Method 1: Standard click
        try:
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await submit_button.click()
            self.logger.info("Submit clicked (standard)")
            return ("standard_click", True)
        except Exception as e:
            self.logger.debug(f"Standard click failed: {str(e)}")

        # Method 2: Force click (bypass overlays)
        try:
            await submit_button.click(force=True)
            self.logger.info("Submit clicked (forced)")
            return ("force_click", True)
        except Exception as e:
            self.logger.debug(f"Force click failed: {str(e)}")

        # Method 3: JavaScript click
        try:
            await submit_button.evaluate("el => el.click()")
            self.logger.info("Submit clicked (JavaScript)")
            return ("javascript_click", True)
        except Exception as e:
            self.logger.debug(f"JavaScript click failed: {str(e)}")

        # Method 4: Dispatch click event
        try:
            await submit_button.dispatch_event("click")
            self.logger.info("Submit clicked (dispatch event)")
            return ("dispatch_click", True)
        except Exception as e:
            self.logger.debug(f"Dispatch event failed: {str(e)}")

        return ("none", False)

    async def _verify_submission_success(self, page: Page) -> Dict:
        """Verify if form submission was successful"""

        # Wait for navigation or success indicators
        await asyncio.sleep(3)

        # Success indicators
        success_indicators = [
            # URL changes
            ("url_change", lambda: "thank" in page.url.lower() or "success" in page.url.lower() or "confirm" in page.url.lower()),

            # Success messages
            ("success_message", lambda: self._check_success_message(page)),

            # Form disappears
            ("form_hidden", lambda: self._check_form_hidden(page)),

            # Thank you page
            ("thank_you_page", lambda: self._check_thank_you_content(page))
        ]

        for method, check_func in success_indicators:
            try:
                # Call the check function properly
                if method == "url_change":
                    result = "thank" in page.url.lower() or "success" in page.url.lower() or "confirm" in page.url.lower()
                elif method == "success_message":
                    result = await self._check_success_message(page)
                elif method == "form_hidden":
                    result = await self._check_form_hidden(page)
                elif method == "thank_you_page":
                    result = await self._check_thank_you_content(page)
                else:
                    continue

                if result:
                    return {"success": True, "method": method}
            except Exception as e:
                self.logger.debug(f"Verification method {method} failed: {str(e)}")
                continue

        # No success indicators found
        return {"success": False, "method": "none", "reason": "No success indicators detected"}

    async def _check_success_message(self, page: Page) -> bool:
        """Check for success message on page"""

        success_patterns = [
            ".success",
            ".success-message",
            ".confirmation",
            ".thank-you",
            "[role='alert'][class*='success']"
        ]

        for pattern in success_patterns:
            try:
                elements = page.locator(pattern)
                if await elements.count() > 0:
                    text = await elements.first.text_content()
                    if text and any(word in text.lower() for word in ['success', 'thank', 'received', 'sent', 'submitted']):
                        self.logger.info(f"Success message found: {text[:100]}")
                        return True
            except:
                continue

        # Check for any visible text with success keywords
        try:
            body_text = await page.text_content("body")
            if body_text:
                text_lower = body_text.lower()
                if ("thank you" in text_lower or
                    "successfully submitted" in text_lower or
                    "we'll be in touch" in text_lower or
                    "we will contact you" in text_lower):
                    return True
        except:
            pass

        return False

    async def _check_form_hidden(self, page: Page) -> bool:
        """Check if form is now hidden (indicates success)"""

        try:
            forms = page.locator("form")
            count = await forms.count()

            if count == 0:
                return True

            # Check if forms are hidden
            for i in range(count):
                form = forms.nth(i)
                if await form.is_visible():
                    return False

            return True
        except:
            return False

    async def _check_thank_you_content(self, page: Page) -> bool:
        """Check for thank you page content"""

        try:
            # Check page title
            title = await page.title()
            if title and any(word in title.lower() for word in ['thank', 'success', 'confirm']):
                return True

            # Check for prominent thank you headings
            headings = page.locator("h1, h2, h3")
            count = await headings.count()

            for i in range(min(count, 5)):
                text = await headings.nth(i).text_content()
                if text and any(word in text.lower() for word in ['thank you', 'success', 'received']):
                    return True

        except:
            pass

        return False
