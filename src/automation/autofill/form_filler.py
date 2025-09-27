"""
Intelligent form filling engine with cascading fallback strategies.
"""

import asyncio
import random
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from playwright.async_api import Page, Locator

from ..forms.simple_form_detector import SimpleFormDetector, SimpleFormResult
from ...models.contact_data import ContactData
from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FillResult:
    """Result of form filling operation"""
    success: bool
    fields_filled: Dict[str, bool]
    error_message: Optional[str] = None
    submit_attempted: bool = False
    submit_success: bool = False


class FormFiller:
    """Intelligent form filler with human-like behavior"""
    
    def __init__(self):
        self.logger = logger
        self.detector = SimpleFormDetector()
        
        # Typing delays to simulate human behavior
        self.typing_delay_range = (50, 150)  # milliseconds
        self.field_delay_range = (500, 1500)  # milliseconds between fields
    
    async def fill_contact_form(
        self, 
        page: Page, 
        contact_data: ContactData,
        submit_form: bool = False
    ) -> FillResult:
        """Fill a contact form with provided data"""
        
        self.logger.info("Starting form fill operation", {
            "operation": "form_fill_start",
            "url": page.url,
            "submit_form": submit_form
        })
        
        try:
            # First detect the form
            form_result = await self.detector.detect_contact_form(page)
            
            if not form_result.success:
                return FillResult(
                    success=False,
                    fields_filled={},
                    error_message="No suitable form detected"
                )
            
            # Map contact data to form fields
            field_mapping = self._map_contact_data_to_fields(contact_data)
            
            # Fill each detected field
            fields_filled = {}
            
            for field_type, form_field in form_result.fields.items():
                if field_type in field_mapping:
                    value = field_mapping[field_type]
                    
                    try:
                        success = await self._fill_field(form_field.element, value)
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
                    await form_result.submit_button.click()
                    submit_success = True
                    self.logger.info("Form submitted successfully")
                    
                    # Wait a moment for submission to process
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Form submission failed: {str(e)}")
                    submit_success = False
            
            success = len([f for f in fields_filled.values() if f]) > 0
            
            self.logger.info("Form fill operation completed", {
                "operation": "form_fill_complete",
                "success": success,
                "fields_filled": sum(fields_filled.values()),
                "total_fields": len(fields_filled),
                "submit_attempted": submit_attempted,
                "submit_success": submit_success
            })
            
            return FillResult(
                success=success,
                fields_filled=fields_filled,
                submit_attempted=submit_attempted,
                submit_success=submit_success
            )
            
        except Exception as e:
            self.logger.error("Form fill operation failed", {
                "operation": "form_fill_error",
                "error": str(e)
            })
            
            return FillResult(
                success=False,
                fields_filled={},
                error_message=str(e)
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
    
    async def _fill_field(self, element: Locator, value: str) -> bool:
        """Fill a single form field with human-like typing"""
        
        try:
            # Clear the field first
            await element.click()
            await element.press("Control+a")  # Select all
            await element.press("Delete")     # Clear
            
            # Type with human-like delays
            for char in value:
                await element.type(char)
                delay = random.randint(*self.typing_delay_range)
                await asyncio.sleep(delay / 1000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Field fill error: {str(e)}")
            return False
    
    async def fill_and_submit(
        self, 
        page: Page, 
        contact_data: ContactData,
        wait_after_submit: int = 3
    ) -> FillResult:
        """Convenience method to fill and submit form in one operation"""
        
        result = await self.fill_contact_form(page, contact_data, submit_form=True)
        
        if result.submit_attempted and wait_after_submit > 0:
            await asyncio.sleep(wait_after_submit)
        
        return result