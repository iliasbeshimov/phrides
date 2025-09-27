"""
Enhanced form filling engine with improved dynamic content handling.
"""

import asyncio
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from playwright.async_api import Page, Locator

from ..forms.enhanced_form_detector import EnhancedFormDetector, EnhancedFormResult
from ...models.contact_data import ContactData
from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EnhancedFillResult:
    """Result of enhanced form filling operation"""
    success: bool
    fields_filled: Dict[str, bool]
    error_message: Optional[str] = None
    submit_attempted: bool = False
    submit_success: bool = False
    is_iframe_form: bool = False
    total_fields_found: int = 0


class EnhancedFormFiller:
    """Enhanced form filler with better dynamic content support"""
    
    def __init__(self):
        self.logger = logger
        self.detector = EnhancedFormDetector()
        
        # More conservative typing delays for stability
        self.typing_delay_range = (80, 200)  # milliseconds
        self.field_delay_range = (1000, 2000)  # milliseconds between fields
    
    async def fill_contact_form(
        self, 
        page: Page, 
        contact_data: ContactData,
        submit_form: bool = False,
        extended_timeout: bool = True
    ) -> EnhancedFillResult:
        """Fill a contact form with enhanced handling"""
        
        self.logger.info("Starting enhanced form fill operation", {
            "operation": "enhanced_form_fill_start",
            "url": page.url,
            "submit_form": submit_form,
            "extended_timeout": extended_timeout
        })
        
        try:
            # Set longer timeouts for dynamic content
            if extended_timeout:
                page.set_default_timeout(20000)  # 20 seconds
            
            # First detect the form
            form_result = await self.detector.detect_contact_form(page)
            
            if not form_result.success:
                return EnhancedFillResult(
                    success=False,
                    fields_filled={},
                    error_message="No suitable form detected",
                    total_fields_found=0
                )
            
            # Map contact data to form fields
            field_mapping = self._map_contact_data_to_fields(contact_data)
            
            # Fill each detected field
            fields_filled = {}
            total_fields = len(form_result.fields)
            
            for field_type, form_field in form_result.fields.items():
                if field_type in field_mapping:
                    value = field_mapping[field_type]
                    
                    try:
                        success = await self._fill_field_enhanced(form_field.element, value, form_result.is_in_iframe)
                        fields_filled[field_type] = success
                        
                        if success:
                            self.logger.debug(f"Successfully filled {field_type}")
                        else:
                            self.logger.warning(f"Failed to fill {field_type}")
                        
                        # Human-like delay between fields
                        delay = random.randint(*self.field_delay_range)
                        await asyncio.sleep(delay / 1000)
                        
                    except Exception as e:
                        self.logger.error(f"Error filling {field_type}: {str(e)}")
                        fields_filled[field_type] = False
            
            # Submit form if requested
            submit_attempted = False
            submit_success = False
            
            if submit_form and form_result.submit_button:
                submit_attempted = True
                try:
                    # Scroll to submit button and wait
                    await form_result.submit_button.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    
                    await form_result.submit_button.click()
                    submit_success = True
                    self.logger.info("Form submitted successfully")
                    
                    # Wait for submission to process
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    self.logger.error(f"Form submission failed: {str(e)}")
                    submit_success = False
            
            success = len([f for f in fields_filled.values() if f]) > 0
            
            self.logger.info("Enhanced form fill operation completed", {
                "operation": "enhanced_form_fill_complete",
                "success": success,
                "fields_filled": sum(fields_filled.values()),
                "total_fields": total_fields,
                "submit_attempted": submit_attempted,
                "submit_success": submit_success,
                "is_iframe_form": form_result.is_in_iframe
            })
            
            return EnhancedFillResult(
                success=success,
                fields_filled=fields_filled,
                submit_attempted=submit_attempted,
                submit_success=submit_success,
                is_iframe_form=form_result.is_in_iframe,
                total_fields_found=total_fields
            )
            
        except Exception as e:
            self.logger.error("Enhanced form fill operation failed", {
                "operation": "enhanced_form_fill_error",
                "error": str(e)
            })
            
            return EnhancedFillResult(
                success=False,
                fields_filled={},
                error_message=str(e),
                total_fields_found=0
            )
    
    def _map_contact_data_to_fields(self, contact_data: ContactData) -> Dict[str, str]:
        """Map contact data to form field types"""
        
        mapping = {}
        
        if contact_data.first_name:
            mapping["first_name"] = contact_data.first_name
        
        if contact_data.last_name:
            mapping["last_name"] = contact_data.last_name
            
        # Full name field (when first/last are combined)
        if contact_data.first_name and contact_data.last_name:
            mapping["name"] = f"{contact_data.first_name} {contact_data.last_name}"
        
        if contact_data.email:
            mapping["email"] = contact_data.email
        
        if contact_data.phone:
            mapping["phone"] = contact_data.phone
        
        # Add a sample zip code for testing
        mapping["zip"] = "90210"
        
        # Create a compelling message about car leasing interest
        if contact_data.preferred_vehicles:
            vehicles = ", ".join(contact_data.preferred_vehicles[:2])
            message = f"Hi, I'm interested in leasing a {vehicles}. Could you please provide more information about your current lease deals and availability? Thank you!"
        else:
            message = "Hi, I'm interested in exploring your current car leasing options. Could you please provide more information about available vehicles and lease terms? Thank you!"
        
        mapping["message"] = message
        
        return mapping
    
    async def _fill_field_enhanced(self, element: Locator, value: str, is_iframe: bool = False) -> bool:
        """Fill a single form field with enhanced error handling"""
        
        try:
            # Wait for element to be ready
            await element.wait_for(state="visible", timeout=5000)
            await element.wait_for(state="attached", timeout=5000)
            
            # Scroll to element
            await element.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            
            # Multiple filling strategies
            strategies = [
                self._fill_strategy_click_and_type,
                self._fill_strategy_focus_and_type,
                self._fill_strategy_direct_fill
            ]
            
            for strategy in strategies:
                try:
                    if await strategy(element, value):
                        return True
                except Exception as e:
                    self.logger.debug(f"Fill strategy failed: {str(e)}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Enhanced field fill error: {str(e)}")
            return False
    
    async def _fill_strategy_click_and_type(self, element: Locator, value: str) -> bool:
        """Strategy 1: Click, clear, and type"""
        
        # Click to focus
        await element.click()
        await asyncio.sleep(0.2)
        
        # Clear existing content
        await element.press("Control+a")
        await element.press("Delete")
        await asyncio.sleep(0.2)
        
        # Type with human-like delays
        for char in value:
            await element.type(char)
            delay = random.randint(*self.typing_delay_range)
            await asyncio.sleep(delay / 1000)
        
        # Verify the value was set
        actual_value = await element.input_value()
        return actual_value.strip() == value.strip()
    
    async def _fill_strategy_focus_and_type(self, element: Locator, value: str) -> bool:
        """Strategy 2: Focus and type"""
        
        await element.focus()
        await asyncio.sleep(0.2)
        
        # Clear and type
        await element.fill("")
        await asyncio.sleep(0.2)
        await element.type(value, delay=100)
        
        # Verify
        actual_value = await element.input_value()
        return actual_value.strip() == value.strip()
    
    async def _fill_strategy_direct_fill(self, element: Locator, value: str) -> bool:
        """Strategy 3: Direct fill"""
        
        await element.fill(value)
        
        # Verify
        actual_value = await element.input_value()
        return actual_value.strip() == value.strip()
    
    async def fill_and_submit(
        self, 
        page: Page, 
        contact_data: ContactData,
        wait_after_submit: int = 5
    ) -> EnhancedFillResult:
        """Convenience method to fill and submit form with enhanced handling"""
        
        result = await self.fill_contact_form(page, contact_data, submit_form=True)
        
        if result.submit_attempted and wait_after_submit > 0:
            await asyncio.sleep(wait_after_submit)
        
        return result