"""
Simplified form detection for immediate testing.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import Page, Locator

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SimpleFormField:
    """Simple form field representation"""
    element: Locator
    field_type: str
    selector: str
    confidence: float


@dataclass  
class SimpleFormResult:
    """Simple form detection result"""
    success: bool
    form_element: Optional[Locator]
    fields: Dict[str, SimpleFormField]
    submit_button: Optional[Locator]
    confidence_score: float


class SimpleFormDetector:
    """Simple form detector for immediate testing"""
    
    def __init__(self):
        self.logger = logger
        
        # Enhanced field selectors for dealership websites
        self.field_selectors = {
            "first_name": [
                "input[name*='first' i]",
                "input[id*='first' i]", 
                "input[placeholder*='first' i]",
                "input[name*='fname' i]",
                "input[id*='fname' i]",
                "#firstName", "#firstname", "#fname", "#first_name",
                "input[name='FirstName']", "input[name='first_name']"
            ],
            "last_name": [
                "input[name*='last' i]",
                "input[id*='last' i]",
                "input[placeholder*='last' i]",
                "input[name*='lname' i]", 
                "input[id*='lname' i]",
                "#lastName", "#lastname", "#lname", "#last_name",
                "input[name='LastName']", "input[name='last_name']"
            ],
            "name": [
                "input[name*='name' i]",
                "input[id*='name' i]",
                "input[placeholder*='name' i]",
                "input[name='Name']", "input[name='name']",
                "#name", "#fullname", "#full_name"
            ],
            "email": [
                "input[type='email']",
                "input[name*='email' i]",
                "input[id*='email' i]",
                "input[placeholder*='email' i]",
                "input[name='Email']", "input[name='email']",
                "#email", "#Email"
            ],
            "phone": [
                "input[type='tel']",
                "input[name*='phone' i]",
                "input[id*='phone' i]",
                "input[placeholder*='phone' i]",
                "input[name*='tel' i]",
                "input[name='Phone']", "input[name='phone']",
                "#phone", "#Phone", "#telephone"
            ],
            "zip": [
                "input[name*='zip' i]",
                "input[id*='zip' i]",
                "input[placeholder*='zip' i]",
                "input[name*='postal' i]",
                "input[name='ZipCode']", "input[name='zip_code']",
                "#zip", "#zipcode", "#postal"
            ],
            "message": [
                "textarea[name*='message' i]",
                "textarea[name*='comment' i]",
                "textarea[id*='message' i]",
                "textarea[placeholder*='message' i]",
                "textarea[name*='inquiry' i]",
                "textarea[name*='question' i]",
                "textarea[name='Message']", "textarea[name='Comments']",
                "textarea", "#message", "#comments"
            ]
        }
    
    async def detect_contact_form(self, page: Page) -> SimpleFormResult:
        """Detect contact form on the page with enhanced dynamic content handling"""
        
        self.logger.info("Starting enhanced form detection", {
            "operation": "enhanced_form_detection_start",
            "url": page.url
        })
        
        try:
            # Wait for page to stabilize and dynamic content to load
            await self._wait_for_dynamic_content(page)
            
            # Check iframes first
            iframe_result = await self._detect_forms_in_iframes(page)
            if iframe_result.success:
                self.logger.info("Found form in iframe", {
                    "operation": "iframe_form_found",
                    "fields_count": len(iframe_result.fields)
                })
                return iframe_result
            
            # Look for forms in main page
            forms = page.locator("form")
            form_count = await forms.count()
            
            self.logger.debug(f"Found {form_count} forms on main page")
            
            best_form = None
            best_fields = {}
            best_score = 0.0
            
            # Check each form
            for i in range(form_count):
                form = forms.nth(i)
                fields = await self._detect_fields_in_form(form)
                score = len(fields) * 0.2  # Simple scoring
                
                if score > best_score:
                    best_score = score
                    best_form = form
                    best_fields = fields
            
            # If no forms found, check the whole page
            if form_count == 0 or best_score < 0.4:
                self.logger.debug("No good forms found, checking whole page")
                page_fields = await self._detect_fields_in_container(page)
                if len(page_fields) > len(best_fields):
                    best_form = None  # No specific form
                    best_fields = page_fields
                    best_score = len(page_fields) * 0.15
            
            # Find submit button
            submit_button = await self._find_submit_button(best_form or page)
            
            success = len(best_fields) >= 2  # Need at least 2 fields
            
            self.logger.info("Enhanced form detection completed", {
                "operation": "enhanced_form_detection_complete",
                "success": success,
                "fields_found": len(best_fields),
                "field_types": list(best_fields.keys()),
                "confidence": best_score,
                "has_submit": submit_button is not None
            })
            
            return SimpleFormResult(
                success=success,
                form_element=best_form,
                fields=best_fields,
                submit_button=submit_button,
                confidence_score=best_score
            )
            
        except Exception as e:
            self.logger.error("Enhanced form detection failed", {
                "operation": "enhanced_form_detection_error",
                "error": str(e)
            })
            
            return SimpleFormResult(
                success=False,
                form_element=None,
                fields={},
                submit_button=None,
                confidence_score=0.0
            )
    
    async def _detect_fields_in_form(self, form: Locator) -> Dict[str, SimpleFormField]:
        """Detect fields within a specific form"""
        fields = {}
        
        for field_type, selectors in self.field_selectors.items():
            field = await self._find_field_by_selectors(form, selectors, field_type)
            if field:
                fields[field_type] = field
        
        return fields
    
    async def _detect_fields_in_container(self, container: Locator) -> Dict[str, SimpleFormField]:
        """Detect fields in any container (page or div)"""
        fields = {}
        
        for field_type, selectors in self.field_selectors.items():
            field = await self._find_field_by_selectors(container, selectors, field_type)
            if field:
                fields[field_type] = field
        
        return fields
    
    async def _find_field_by_selectors(self, container: Locator, selectors: List[str], field_type: str) -> Optional[SimpleFormField]:
        """Find field using multiple selectors"""
        
        for selector in selectors:
            try:
                elements = container.locator(selector)
                count = await elements.count()
                
                if count > 0:
                    element = elements.first
                    
                    # Check if it's actually a form field
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea", "select"]:
                        return SimpleFormField(
                            element=element,
                            field_type=field_type,
                            selector=selector,
                            confidence=0.8
                        )
            except Exception as e:
                self.logger.debug(f"Selector failed: {selector} - {str(e)}")
                continue
        
        return None
    
    async def _wait_for_dynamic_content(self, page: Page) -> None:
        """Wait for dynamic content to load"""
        
        # Wait for common JavaScript frameworks to load
        await asyncio.sleep(2)  # Initial wait
        
        # Wait for common loading indicators to disappear
        loading_selectors = [
            ".loading", ".spinner", ".loader", 
            "[data-loading]", ".sk-loading",
            ".fa-spinner", ".fa-circle-o-notch"
        ]
        
        for selector in loading_selectors:
            try:
                await page.wait_for_selector(selector, state="hidden", timeout=3000)
            except:
                continue
        
        # Wait for forms or inputs to appear
        try:
            await page.wait_for_selector("form, input, textarea", timeout=5000)
        except:
            pass  # Continue if no forms appear
        
        # Additional wait for form rendering
        await asyncio.sleep(1)
    
    async def _detect_forms_in_iframes(self, page: Page) -> SimpleFormResult:
        """Detect forms within iframes on the page"""
        
        try:
            # Find all iframes
            iframes = page.locator("iframe")
            iframe_count = await iframes.count()
            
            if iframe_count == 0:
                return SimpleFormResult(False, None, {}, None, 0.0)
            
            self.logger.debug(f"Found {iframe_count} iframes to check")
            
            for i in range(iframe_count):
                try:
                    iframe = iframes.nth(i)
                    frame = await iframe.content_frame()
                    
                    if frame is None:
                        continue
                    
                    # Wait for iframe content to load
                    await asyncio.sleep(1)
                    
                    # Check for forms in the iframe
                    forms = frame.locator("form")
                    form_count = await forms.count()
                    
                    if form_count > 0:
                        # Analyze forms in iframe
                        for j in range(form_count):
                            form = forms.nth(j)
                            fields = await self._detect_fields_in_iframe_form(frame, form)
                            
                            if len(fields) >= 2:
                                submit_button = await self._find_submit_button_in_frame(frame, form)
                                
                                return SimpleFormResult(
                                    success=True,
                                    form_element=form,
                                    fields=fields,
                                    submit_button=submit_button,
                                    confidence_score=len(fields) * 0.25
                                )
                
                except Exception as e:
                    self.logger.debug(f"Error checking iframe {i}: {str(e)}")
                    continue
            
            return SimpleFormResult(False, None, {}, None, 0.0)
            
        except Exception as e:
            self.logger.error(f"Iframe detection failed: {str(e)}")
            return SimpleFormResult(False, None, {}, None, 0.0)
    
    async def _detect_fields_in_iframe_form(self, frame, form: Locator) -> Dict[str, SimpleFormField]:
        """Detect fields within an iframe form"""
        fields = {}
        
        for field_type, selectors in self.field_selectors.items():
            field = await self._find_field_by_selectors_in_frame(frame, form, selectors, field_type)
            if field:
                fields[field_type] = field
        
        return fields
    
    async def _find_field_by_selectors_in_frame(self, frame, container: Locator, selectors: List[str], field_type: str) -> Optional[SimpleFormField]:
        """Find field using multiple selectors within iframe"""
        
        for selector in selectors:
            try:
                elements = container.locator(selector)
                count = await elements.count()
                
                if count > 0:
                    element = elements.first
                    
                    # Check if it's actually a form field
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea", "select"]:
                        return SimpleFormField(
                            element=element,
                            field_type=field_type,
                            selector=selector,
                            confidence=0.8
                        )
            except Exception as e:
                self.logger.debug(f"Iframe selector failed: {selector} - {str(e)}")
                continue
        
        return None
    
    async def _find_submit_button_in_frame(self, frame, container: Locator) -> Optional[Locator]:
        """Find submit button within iframe"""
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:text('Submit')",
            "button:text('Send')",
            "button:text('Contact')",
            "button:text('Get Quote')",
            ".submit-btn",
            "#submit"
        ]
        
        for selector in submit_selectors:
            try:
                buttons = container.locator(selector)
                if await buttons.count() > 0:
                    return buttons.first
            except Exception:
                continue
        
        return None
    
    async def _find_submit_button(self, container: Locator) -> Optional[Locator]:
        """Find submit button"""
        
        # Try different submit button selectors
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:text('Submit')",
            "button:text('Send')",
            "button:text('Contact')",
            "button:text('Get Quote')",
            ".submit-btn",
            "#submit"
        ]
        
        for selector in submit_selectors:
            try:
                buttons = container.locator(selector)
                if await buttons.count() > 0:
                    return buttons.first
            except Exception:
                continue
        
        return None
    
    async def _wait_for_dynamic_content(self, page: Page) -> None:
        """Wait for dynamic content to load"""
        
        # Wait for common JavaScript frameworks to load
        await asyncio.sleep(2)  # Initial wait
        
        # Wait for common loading indicators to disappear
        loading_selectors = [
            ".loading", ".spinner", ".loader", 
            "[data-loading]", ".sk-loading",
            ".fa-spinner", ".fa-circle-o-notch"
        ]
        
        for selector in loading_selectors:
            try:
                await page.wait_for_selector(selector, state="hidden", timeout=3000)
            except:
                continue
        
        # Wait for forms or inputs to appear
        try:
            await page.wait_for_selector("form, input, textarea", timeout=5000)
        except:
            pass  # Continue if no forms appear
        
        # Additional wait for form rendering
        await asyncio.sleep(1)
    
    async def _detect_forms_in_iframes(self, page: Page) -> SimpleFormResult:
        """Detect forms within iframes on the page"""
        
        try:
            # Find all iframes
            iframes = page.locator("iframe")
            iframe_count = await iframes.count()
            
            if iframe_count == 0:
                return SimpleFormResult(False, None, {}, None, 0.0)
            
            self.logger.debug(f"Found {iframe_count} iframes to check")
            
            for i in range(iframe_count):
                try:
                    iframe = iframes.nth(i)
                    frame = await iframe.content_frame()
                    
                    if frame is None:
                        continue
                    
                    # Wait for iframe content to load
                    await asyncio.sleep(1)
                    
                    # Check for forms in the iframe
                    forms = frame.locator("form")
                    form_count = await forms.count()
                    
                    if form_count > 0:
                        # Analyze forms in iframe
                        for j in range(form_count):
                            form = forms.nth(j)
                            fields = await self._detect_fields_in_iframe_form(frame, form)
                            
                            if len(fields) >= 2:
                                submit_button = await self._find_submit_button_in_frame(frame, form)
                                
                                return SimpleFormResult(
                                    success=True,
                                    form_element=form,
                                    fields=fields,
                                    submit_button=submit_button,
                                    confidence_score=len(fields) * 0.25
                                )
                
                except Exception as e:
                    self.logger.debug(f"Error checking iframe {i}: {str(e)}")
                    continue
            
            return SimpleFormResult(False, None, {}, None, 0.0)
            
        except Exception as e:
            self.logger.error(f"Iframe detection failed: {str(e)}")
            return SimpleFormResult(False, None, {}, None, 0.0)
    
    async def _detect_fields_in_iframe_form(self, frame, form: Locator) -> Dict[str, SimpleFormField]:
        """Detect fields within an iframe form"""
        fields = {}
        
        for field_type, selectors in self.field_selectors.items():
            field = await self._find_field_by_selectors_in_frame(frame, form, selectors, field_type)
            if field:
                fields[field_type] = field
        
        return fields
    
    async def _find_field_by_selectors_in_frame(self, frame, container: Locator, selectors: List[str], field_type: str) -> Optional[SimpleFormField]:
        """Find field using multiple selectors within iframe"""
        
        for selector in selectors:
            try:
                elements = container.locator(selector)
                count = await elements.count()
                
                if count > 0:
                    element = elements.first
                    
                    # Check if it's actually a form field
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea", "select"]:
                        return SimpleFormField(
                            element=element,
                            field_type=field_type,
                            selector=selector,
                            confidence=0.8
                        )
            except Exception as e:
                self.logger.debug(f"Iframe selector failed: {selector} - {str(e)}")
                continue
        
        return None
    
    async def _find_submit_button_in_frame(self, frame, container: Locator) -> Optional[Locator]:
        """Find submit button within iframe"""
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:text('Submit')",
            "button:text('Send')",
            "button:text('Contact')",
            "button:text('Get Quote')",
            ".submit-btn",
            "#submit"
        ]
        
        for selector in submit_selectors:
            try:
                buttons = container.locator(selector)
                if await buttons.count() > 0:
                    return buttons.first
            except Exception:
                continue
        
        return None