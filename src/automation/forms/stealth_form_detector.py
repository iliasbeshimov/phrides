"""
Stealth form detector that minimizes DOM queries to avoid Cloudflare detection.
Uses single-pass detection with minimal scanning patterns.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
from playwright.async_api import Page, Locator


@dataclass
class StealthFormField:
    """Simplified form field representation."""
    selector: str
    field_type: str
    confidence: float


@dataclass
class StealthFormResult:
    """Simplified form detection result."""
    success: bool
    form_selector: Optional[str]
    fields: Dict[str, StealthFormField]
    submit_selector: Optional[str]
    detection_method: str


class StealthFormDetector:
    """Minimal form detector to avoid triggering security systems."""

    def __init__(self):
        # Simplified, high-confidence selectors only
        self.quick_form_selectors = [
            'form',
            '[role="form"]',
            '.contact-form',
            '.gform_wrapper form',
            '.wpcf7-form'
        ]

        # High-confidence field patterns
        self.field_patterns = {
            'first_name': [
                'input[name*="first"]',
                'input[id*="first"]',
                'input[placeholder*="First"]'
            ],
            'last_name': [
                'input[name*="last"]',
                'input[id*="last"]',
                'input[placeholder*="Last"]'
            ],
            'email': [
                'input[type="email"]',
                'input[name*="email"]',
                'input[id*="email"]'
            ],
            'phone': [
                'input[type="tel"]',
                'input[name*="phone"]',
                'input[id*="phone"]'
            ],
            'message': [
                'textarea[name*="message"]',
                'textarea[name*="comment"]',
                'textarea[id*="message"]'
            ]
        }

        self.submit_patterns = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")'
        ]

    async def detect_form_quickly(self, page: Page) -> StealthFormResult:
        """
        Single-pass form detection with minimal DOM queries.
        Designed to avoid detection by security systems.
        """
        try:
            # Wait for page to be ready (but not too long)
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
            await asyncio.sleep(1.0)  # Brief pause for dynamic content

            # Single attempt to find form
            form_locator = await self._find_form_quickly(page)
            if not form_locator:
                return StealthFormResult(
                    success=False,
                    form_selector=None,
                    fields={},
                    submit_selector=None,
                    detection_method="no_form_found"
                )

            # Quick field detection within form context
            fields = await self._detect_fields_quickly(form_locator)
            submit_selector = await self._find_submit_quickly(form_locator)

            # Minimum viable form check - be more permissive for stealth
            required_fields = ['email']  # At minimum need email
            has_required = any(field_type in fields for field_type in required_fields)

            # Allow forms with any contact field, not just email
            contact_fields = ['email', 'phone', 'first_name', 'last_name', 'message']
            has_contact_field = any(field_type in fields for field_type in contact_fields)

            if not has_contact_field:
                return StealthFormResult(
                    success=False,
                    form_selector=None,
                    fields=fields,
                    submit_selector=submit_selector,
                    detection_method="insufficient_fields"
                )

            return StealthFormResult(
                success=True,
                form_selector=await self._get_form_selector(form_locator),
                fields=fields,
                submit_selector=submit_selector,
                detection_method="quick_detection"
            )

        except Exception as exc:
            return StealthFormResult(
                success=False,
                form_selector=None,
                fields={},
                submit_selector=None,
                detection_method=f"error: {exc}"
            )

    async def _find_form_quickly(self, page: Page) -> Optional[Locator]:
        """Find form with minimal queries."""
        for selector in self.quick_form_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0:
                    return locator
            except Exception:
                continue
        return None

    async def _detect_fields_quickly(self, form_locator: Locator) -> Dict[str, StealthFormField]:
        """Detect fields with single queries per type."""
        fields = {}

        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                try:
                    field_locator = form_locator.locator(pattern).first
                    if await field_locator.count() > 0:
                        fields[field_type] = StealthFormField(
                            selector=pattern,
                            field_type=field_type,
                            confidence=0.9  # High confidence for matched patterns
                        )
                        break  # Found field, move to next type
                except Exception:
                    continue

        return fields

    async def _find_submit_quickly(self, form_locator: Locator) -> Optional[str]:
        """Find submit button with minimal queries."""
        for pattern in self.submit_patterns:
            try:
                submit_locator = form_locator.locator(pattern).first
                if await submit_locator.count() > 0:
                    return pattern
            except Exception:
                continue
        return None

    async def _get_form_selector(self, form_locator: Locator) -> str:
        """Get minimal form selector."""
        try:
            # Try to get a simple, stable selector
            element = await form_locator.element_handle()
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')

            if tag_name == 'form':
                return 'form'

            # Check for common form classes
            class_name = await element.evaluate('el => el.className')
            if 'contact-form' in class_name:
                return '.contact-form'
            elif 'gform_wrapper' in class_name:
                return '.gform_wrapper form'
            elif 'wpcf7-form' in class_name:
                return '.wpcf7-form'

            return 'form'  # Default fallback

        except Exception:
            return 'form'


class MinimalFormSubmissionPipeline:
    """
    Simplified submission pipeline that minimizes detection risk.
    Focus on speed and stealth over comprehensive detection.
    """

    def __init__(self):
        self.detector = StealthFormDetector()

    async def execute_stealth_submission(
        self,
        page: Page,
        contact_data: dict
    ) -> dict:
        """
        Execute form submission with minimal footprint.
        Returns basic success/failure status.
        """
        result = {
            'success': False,
            'detection_time': 0,
            'filling_time': 0,
            'submission_time': 0,
            'method': 'stealth_pipeline',
            'fields_filled': [],
            'errors': []
        }

        try:
            # Phase 1: Quick Detection (< 5 seconds)
            detection_start = asyncio.get_event_loop().time()
            form_result = await self.detector.detect_form_quickly(page)
            result['detection_time'] = asyncio.get_event_loop().time() - detection_start

            if not form_result.success:
                result['errors'].append(f"Detection failed: {form_result.detection_method}")
                return result

            # Phase 2: Minimal Form Filling (natural timing)
            filling_start = asyncio.get_event_loop().time()
            filled_fields = await self._fill_essential_fields_only(
                page, form_result.fields, contact_data
            )
            result['filling_time'] = asyncio.get_event_loop().time() - filling_start
            result['fields_filled'] = filled_fields

            if not filled_fields:
                result['errors'].append("No fields could be filled")
                return result

            # Phase 3: Submit (if we have submit button)
            if form_result.submit_selector:
                submission_start = asyncio.get_event_loop().time()
                submitted = await self._submit_form_quickly(page, form_result.submit_selector)
                result['submission_time'] = asyncio.get_event_loop().time() - submission_start

                if submitted:
                    result['success'] = True
                else:
                    result['errors'].append("Submission failed")
            else:
                result['errors'].append("No submit button found")

            return result

        except Exception as exc:
            result['errors'].append(f"Pipeline error: {exc}")
            return result

    async def _fill_essential_fields_only(
        self,
        page: Page,
        fields: Dict[str, StealthFormField],
        contact_data: dict
    ) -> List[str]:
        """Fill only the most essential fields to minimize interaction time."""
        filled_fields = []

        # Priority order: focus on fields most likely to be required
        priority_fields = ['email', 'first_name', 'last_name', 'message']

        for field_type in priority_fields:
            if field_type not in fields or field_type not in contact_data:
                continue

            field = fields[field_type]
            value = contact_data[field_type]

            try:
                # Simple, fast filling without fancy timing
                locator = page.locator(field.selector).first
                await locator.wait_for(timeout=3000)
                await locator.click()
                await locator.fill(str(value))

                filled_fields.append(field_type)

                # Brief pause between fields
                await asyncio.sleep(0.5)

            except Exception:
                continue  # Skip failed fields, continue with others

        return filled_fields

    async def _submit_form_quickly(self, page: Page, submit_selector: str) -> bool:
        """Submit form with minimal interaction."""
        try:
            submit_button = page.locator(submit_selector).first
            await submit_button.wait_for(timeout=3000)
            await submit_button.click()

            # Brief wait for submission to process
            await asyncio.sleep(2.0)
            return True

        except Exception:
            return False