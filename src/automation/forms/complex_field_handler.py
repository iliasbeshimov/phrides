"""
Complex field handler for split fields (phone numbers) and Gravity Forms complex structures.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from playwright.async_api import Page, Locator
from dataclasses import dataclass

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SplitPhoneField:
    """Represents a phone number split across multiple inputs"""
    area_code: Locator
    prefix: Locator
    suffix: Locator
    area_code_selector: str
    prefix_selector: str
    suffix_selector: str


@dataclass
class ComplexNameField:
    """Represents a name field with separate first/last inputs"""
    first_name: Locator
    last_name: Locator
    first_name_selector: str
    last_name_selector: str


class ComplexFieldHandler:
    """Handles complex field patterns like split phone numbers and Gravity Forms structures"""

    def __init__(self):
        self.logger = logger

    async def detect_split_phone_field(self, page: Page) -> Optional[SplitPhoneField]:
        """
        Detect phone number fields split into area code, prefix, and suffix.
        Common patterns:
        - Three consecutive text inputs near "Phone" label
        - Inputs with max length 3, 3, 4 or similar attributes
        - Three small consecutive inputs visually grouped together
        """
        try:
            # Look for phone field containers with JavaScript
            phone_containers = await page.evaluate("""
                () => {
                    const containers = [];

                    // Strategy 1: Look for labels with "Phone" text
                    const labels = Array.from(document.querySelectorAll('label, div, span, td'));

                    for (const label of labels) {
                        const text = (label.textContent || '').toLowerCase().trim();

                        // Must contain "phone" but not be too long (avoid whole paragraphs)
                        if ((text.includes('phone') || text.includes('telephone')) && text.length < 50) {
                            // Find parent container
                            let container = label.closest('.form-group, .field, .gfield, li, div, tr, td, table');
                            if (!container) {
                                container = label.parentElement;
                            }

                            if (container) {
                                // Get all text/tel inputs in this container
                                const inputs = Array.from(container.querySelectorAll('input[type="text"], input[type="tel"], input:not([type])'));

                                // Look for exactly 3 inputs OR 4 inputs (sometimes phone label has its own input)
                                if (inputs.length >= 3 && inputs.length <= 5) {
                                    // Filter out obviously wrong inputs (hidden, very large, etc)
                                    const visibleInputs = inputs.filter(inp => {
                                        const style = window.getComputedStyle(inp);
                                        return style.display !== 'none' &&
                                               style.visibility !== 'hidden' &&
                                               inp.type !== 'hidden';
                                    });

                                    // Try to find 3 consecutive small inputs
                                    for (let i = 0; i <= visibleInputs.length - 3; i++) {
                                        const candidates = visibleInputs.slice(i, i + 3);

                                        // Check if these look like phone inputs
                                        const maxLengths = candidates.map(inp => inp.getAttribute('maxlength'));
                                        const sizes = candidates.map(inp => inp.getAttribute('size'));

                                        // Accept if:
                                        // 1. Has maxlength attributes that match 3-3-4 or 3-4-4 pattern
                                        // 2. OR has small size attributes
                                        // 3. OR inputs are visually small (< 100px wide)
                                        const hasGoodMaxLengths = maxLengths.filter(m => m === '3' || m === '4').length >= 2;
                                        const hasSmallSizes = sizes.filter(s => s && parseInt(s) <= 10).length >= 2;

                                        const widths = candidates.map(inp => {
                                            const style = window.getComputedStyle(inp);
                                            return parseFloat(style.width) || 0;
                                        });
                                        const hasSmallWidths = widths.filter(w => w > 0 && w < 100).length >= 2;

                                        if (hasGoodMaxLengths || hasSmallSizes || hasSmallWidths) {
                                            containers.push({
                                                areaCode: candidates[0].name || candidates[0].id || candidates[0].getAttribute('data-field') || '',
                                                prefix: candidates[1].name || candidates[1].id || candidates[1].getAttribute('data-field') || '',
                                                suffix: candidates[2].name || candidates[2].id || candidates[2].getAttribute('data-field') || '',
                                                foundBy: hasGoodMaxLengths ? 'maxlength' : (hasSmallSizes ? 'size' : 'width')
                                            });
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    return containers;
                }
            """)

            if phone_containers and len(phone_containers) > 0:
                container = phone_containers[0]

                # Build selectors - try ID first, then name
                def build_selector(identifier: str) -> str:
                    if not identifier:
                        return ""
                    # CSS selectors need colons escaped: phone:1 -> phone\\:1
                    # Use name attribute selector which is more reliable
                    return f"[name='{identifier}']"

                area_selector = build_selector(container['areaCode'])
                prefix_selector = build_selector(container['prefix'])
                suffix_selector = build_selector(container['suffix'])

                if not area_selector or not prefix_selector or not suffix_selector:
                    self.logger.debug("Could not build selectors from split phone container")
                    return None

                area_loc = page.locator(area_selector)
                prefix_loc = page.locator(prefix_selector)
                suffix_loc = page.locator(suffix_selector)

                # Verify all three exist
                if await area_loc.count() > 0 and await prefix_loc.count() > 0 and await suffix_loc.count() > 0:
                    self.logger.info("Detected split phone field", {
                        "operation": "split_phone_detected",
                        "area_code": area_selector,
                        "prefix": prefix_selector,
                        "suffix": suffix_selector
                    })

                    return SplitPhoneField(
                        area_code=area_loc.first,
                        prefix=prefix_loc.first,
                        suffix=suffix_loc.first,
                        area_code_selector=area_selector,
                        prefix_selector=prefix_selector,
                        suffix_selector=suffix_selector
                    )

            return None

        except Exception as e:
            self.logger.debug(f"Split phone field detection failed: {str(e)}")
            return None

    async def detect_gravity_forms_complex_name(self, page: Page) -> Optional[ComplexNameField]:
        """
        Detect Gravity Forms complex name fields with sub-labels.
        Pattern: Parent label "Name*" followed by two inputs with sub-labels "First" and "Last"
        """
        try:
            # Look for Gravity Forms name pattern
            name_fields = await page.evaluate("""
                () => {
                    const fields = [];

                    // Look for Gravity Forms name field containers
                    const nameContainers = document.querySelectorAll('.gfield--type-name, [class*="name_"]');

                    for (const container of nameContainers) {
                        const firstInput = container.querySelector('.name_first input, input[id*="_3"]');
                        const lastInput = container.querySelector('.name_last input, input[id*="_6"]');

                        if (firstInput && lastInput) {
                            fields.push({
                                firstName: firstInput.id || firstInput.name || '',
                                firstNameSelector: firstInput.id ? `#${firstInput.id}` : `[name="${firstInput.name}"]`,
                                lastName: lastInput.id || lastInput.name || '',
                                lastNameSelector: lastInput.id ? `#${lastInput.id}` : `[name="${lastInput.name}"]`
                            });
                        }
                    }

                    // Also check for generic pattern: container with "Name" label and two inputs
                    if (fields.length === 0) {
                        const labels = Array.from(document.querySelectorAll('label'));
                        for (const label of labels) {
                            const text = (label.textContent || '').toLowerCase().trim();
                            if (text === 'name' || text === 'name*') {
                                // Look for container with two inputs
                                let container = label.closest('.gfield, .field, .form-group, li, div');
                                if (container) {
                                    const inputs = Array.from(container.querySelectorAll('input[type="text"]'));
                                    if (inputs.length >= 2) {
                                        // Check for First/Last sub-labels
                                        const firstInput = inputs[0];
                                        const lastInput = inputs[1];

                                        const firstLabel = firstInput.parentElement?.querySelector('label');
                                        const lastLabel = lastInput.parentElement?.querySelector('label');

                                        const firstText = (firstLabel?.textContent || '').toLowerCase();
                                        const lastText = (lastLabel?.textContent || '').toLowerCase();

                                        if (firstText.includes('first') && lastText.includes('last')) {
                                            fields.push({
                                                firstName: firstInput.id || firstInput.name || '',
                                                firstNameSelector: firstInput.id ? `#${firstInput.id}` : `[name="${firstInput.name}"]`,
                                                lastName: lastInput.id || lastInput.name || '',
                                                lastNameSelector: lastInput.id ? `#${lastInput.id}` : `[name="${lastInput.name}"]`
                                            });
                                        }
                                    }
                                }
                            }
                        }
                    }

                    return fields;
                }
            """)

            if name_fields and len(name_fields) > 0:
                field = name_fields[0]

                first_loc = page.locator(field['firstNameSelector'])
                last_loc = page.locator(field['lastNameSelector'])

                if await first_loc.count() > 0 and await last_loc.count() > 0:
                    self.logger.info("Detected Gravity Forms complex name field", {
                        "operation": "complex_name_detected",
                        "first_name": field['firstNameSelector'],
                        "last_name": field['lastNameSelector']
                    })

                    return ComplexNameField(
                        first_name=first_loc.first,
                        last_name=last_loc.first,
                        first_name_selector=field['firstNameSelector'],
                        last_name_selector=field['lastNameSelector']
                    )

            return None

        except Exception as e:
            self.logger.debug(f"Complex name field detection failed: {str(e)}")
            return None

    async def detect_gravity_forms_zip_code(self, page: Page) -> Optional[Locator]:
        """
        Detect Gravity Forms zip code field that may not be caught by standard selectors.
        Looks for fields with "Zip Code" label followed by text input.
        """
        try:
            zip_selector = await page.evaluate("""
                () => {
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        const text = (label.textContent || '').toLowerCase().trim();
                        if (text.includes('zip') || text === 'zip code' || text === 'zip code*') {
                            // Find associated input
                            const forAttr = label.getAttribute('for');
                            if (forAttr) {
                                const input = document.getElementById(forAttr);
                                if (input) {
                                    return input.id ? `#${input.id}` : `[name="${input.name}"]`;
                                }
                            }

                            // Look in parent container
                            let container = label.closest('.gfield, .field, .form-group, li, div');
                            if (container) {
                                const input = container.querySelector('input[type="text"]');
                                if (input) {
                                    return input.id ? `#${input.id}` : `[name="${input.name}"]`;
                                }
                            }
                        }
                    }
                    return null;
                }
            """)

            if zip_selector:
                zip_loc = page.locator(zip_selector)
                if await zip_loc.count() > 0:
                    self.logger.info("Detected Gravity Forms zip code field", {
                        "operation": "gravity_zip_detected",
                        "selector": zip_selector
                    })
                    return zip_loc.first

            return None

        except Exception as e:
            self.logger.debug(f"Gravity Forms zip detection failed: {str(e)}")
            return None

    async def fill_split_phone_field(self, split_field: SplitPhoneField, phone_number: str) -> bool:
        """
        Fill a split phone field with a phone number.
        Formats: "1234567890", "(123) 456-7890", "123-456-7890"
        """
        try:
            # Extract digits only
            digits = re.sub(r'\D', '', phone_number)

            if len(digits) == 10:
                area_code = digits[0:3]
                prefix = digits[3:6]
                suffix = digits[6:10]
            elif len(digits) == 11 and digits[0] == '1':
                # Strip leading 1
                area_code = digits[1:4]
                prefix = digits[4:7]
                suffix = digits[7:11]
            else:
                self.logger.warning("Invalid phone number format", {
                    "operation": "split_phone_fill_error",
                    "phone": phone_number,
                    "digits": len(digits)
                })
                return False

            # Fill each field
            await split_field.area_code.fill(area_code)
            await asyncio.sleep(0.2)

            await split_field.prefix.fill(prefix)
            await asyncio.sleep(0.2)

            await split_field.suffix.fill(suffix)
            await asyncio.sleep(0.2)

            self.logger.info("Filled split phone field", {
                "operation": "split_phone_filled",
                "area_code": area_code,
                "prefix": prefix,
                "suffix": suffix
            })

            return True

        except Exception as e:
            self.logger.error(f"Failed to fill split phone field: {str(e)}")
            return False

    async def fill_complex_name_field(self, complex_field: ComplexNameField, first_name: str, last_name: str) -> bool:
        """Fill a complex name field with first and last name"""
        try:
            await complex_field.first_name.fill(first_name)
            await asyncio.sleep(0.2)

            await complex_field.last_name.fill(last_name)
            await asyncio.sleep(0.2)

            self.logger.info("Filled complex name field", {
                "operation": "complex_name_filled",
                "first_name": first_name,
                "last_name": last_name
            })

            return True

        except Exception as e:
            self.logger.error(f"Failed to fill complex name field: {str(e)}")
            return False
