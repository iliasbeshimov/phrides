"""
Amazon Nova Act integration for complex form filling scenarios.
Acts as the ultimate fallback when traditional automation fails.
"""

import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from playwright.async_api import Page

from ...utils.logging import get_logger
from ...core.models.contact_request import ContactRequest

logger = get_logger(__name__)


@dataclass 
class NovaActStep:
    """Represents a single step taken by Nova Act"""
    step_number: int
    action: str
    description: str
    screenshot_before: Optional[str]
    screenshot_after: Optional[str]
    success: bool
    error: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class NovaActResult:
    """Result of Nova Act automation attempt"""
    success: bool
    steps_taken: List[NovaActStep]
    final_state: str
    errors: List[str]
    screenshots: List[str]
    duration_seconds: float
    form_submitted: bool
    confirmation_detected: bool
    metadata: Dict[str, Any]


class NovaActClient:
    """Client for interacting with Amazon Nova Act"""
    
    def __init__(self, aws_region: str = "us-east-1"):
        self.aws_region = aws_region
        self.bedrock_client = boto3.client("bedrock-runtime", region_name=aws_region)
        self.model_id = "amazon.nova-act-v1:0"  # Latest Nova Act model
        self.logger = logger
    
    async def execute_form_filling_task(
        self, 
        page: Page, 
        contact_request: ContactRequest,
        max_steps: int = 25,
        timeout_seconds: int = 120
    ) -> NovaActResult:
        """Execute form filling using Nova Act"""
        
        start_time = datetime.now()
        request_id = f"nova_{int(start_time.timestamp())}"
        
        self.logger.info("Starting Nova Act form filling", {
            "operation": "nova_act_start",
            "request_id": request_id,
            "url": page.url,
            "max_steps": max_steps,
            "timeout": timeout_seconds
        })
        
        try:
            # Take initial screenshot
            initial_screenshot = await page.screenshot(full_page=True)
            
            # Prepare context and instructions
            context = self._prepare_context(contact_request, page.url)
            instructions = self._generate_instructions(contact_request)
            
            # Execute Nova Act automation
            result = await self._execute_nova_act_automation(
                page=page,
                context=context,
                instructions=instructions,
                initial_screenshot=initial_screenshot,
                max_steps=max_steps,
                timeout_seconds=timeout_seconds,
                request_id=request_id
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            result.duration_seconds = duration
            
            self.logger.info("Nova Act execution completed", {
                "operation": "nova_act_complete",
                "request_id": request_id,
                "success": result.success,
                "steps_taken": len(result.steps_taken),
                "duration_seconds": duration,
                "form_submitted": result.form_submitted
            })
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.error("Nova Act execution failed", {
                "operation": "nova_act_error",
                "request_id": request_id,
                "error": str(e),
                "duration_seconds": duration
            })
            
            return NovaActResult(
                success=False,
                steps_taken=[],
                final_state="error",
                errors=[str(e)],
                screenshots=[],
                duration_seconds=duration,
                form_submitted=False,
                confirmation_detected=False,
                metadata={"error": str(e)}
            )
    
    def _prepare_context(self, contact_request: ContactRequest, url: str) -> Dict[str, Any]:
        """Prepare context information for Nova Act"""
        
        return {
            "task_type": "dealership_contact_form",
            "website_url": url,
            "user_data": {
                "first_name": contact_request.user_info.first_name,
                "last_name": contact_request.user_info.last_name,
                "email": contact_request.user_info.email,
                "phone": contact_request.user_info.phone,
                "vehicle_interest": "Jeep",
                "message": contact_request.custom_message,
                "preferred_contact": contact_request.user_info.preferred_contact_method
            },
            "success_criteria": {
                "form_submitted": True,
                "confirmation_received": True,
                "no_errors": True
            },
            "constraints": {
                "respectful_automation": True,
                "no_spam_behavior": True,
                "follow_site_terms": True
            }
        }
    
    def _generate_instructions(self, contact_request: ContactRequest) -> str:
        """Generate detailed instructions for Nova Act"""
        
        user_info = contact_request.user_info
        
        return f"""
You are helping to fill out a car dealership contact form. Your goal is to successfully submit a legitimate inquiry about Jeep vehicles.

CRITICAL SUCCESS CRITERIA:
1. Locate and fill out the main contact/inquiry form on this dealership website
2. Successfully submit the form 
3. Confirm submission was successful (look for confirmation message/page)

USER INFORMATION TO ENTER:
- First Name: {user_info.first_name}
- Last Name: {user_info.last_name}
- Email: {user_info.email}
- Phone: {user_info.phone}
- Vehicle Interest: Jeep (select from dropdown if available)
- Message: {contact_request.custom_message}

DETAILED INSTRUCTIONS:

1. FORM IDENTIFICATION:
   - Look for contact forms, inquiry forms, or "Get Quote" forms
   - Avoid login forms, newsletter signups, or search forms
   - The main contact form is usually prominently displayed
   - Common form titles: "Contact Us", "Get a Quote", "Request Information", "Inquiry Form"

2. FORM FILLING PROCESS:
   - Fill first name field with: {user_info.first_name}
   - Fill last name field with: {user_info.last_name}
   - Fill email field with: {user_info.email}
   - Fill phone field with: {user_info.phone}
   - If there's a vehicle interest dropdown, select "Jeep" or closest option
   - Fill message/comments field with: {contact_request.custom_message}

3. DROPDOWN HANDLING:
   - For vehicle interest: Look for "Jeep", "All Jeep Models", "Jeep Vehicles", or "SUV"
   - For contact preference: Choose "Email" if available
   - For time to contact: Choose "Anytime" or "Business Hours"

4. CHECKBOXES AND AGREEMENTS:
   - Check any required consent boxes (privacy policy, terms of service)
   - Check boxes for "I agree to be contacted" or similar
   - DO NOT check boxes for newsletters unless they seem required

5. FORM SUBMISSION:
   - Click the submit button (usually labeled "Submit", "Send", "Contact Dealer", "Get Quote")
   - Wait for the page to process the submission
   - Look for confirmation messages like "Thank you", "We'll contact you", "Message sent"

6. VERIFICATION:
   - After submission, look for success indicators:
     * Confirmation message displayed
     * Page redirect to thank you page
     * Success banner or notification
   - If you see an error, try to resolve it (e.g., fill missing required fields)

7. SPECIAL CASES TO HANDLE:
   - If CAPTCHA appears: Report that manual intervention is needed
   - If required fields are missing: Fill them with appropriate defaults
   - If form validation fails: Check error messages and correct
   - If multiple forms exist: Choose the main contact/inquiry form

8. TROUBLESHOOTING:
   - If fields won't accept text: Try clicking them first, check if they're enabled
   - If dropdown won't open: Try different click methods (hover, double-click)
   - If submit fails: Check for validation errors, missing required fields
   - If page doesn't respond: Wait a few seconds and try again

IMPORTANT CONSTRAINTS:
- Be respectful and follow the website's intended use
- Don't spam or submit multiple forms
- Don't bypass security measures inappropriately
- Stop if you encounter serious technical issues
- Report any CAPTCHA or anti-bot measures encountered

SUCCESS INDICATORS:
- Form successfully filled with all provided information
- Form submitted without errors
- Confirmation message or success page displayed
- No error messages or validation failures

Take your time and be thorough. Document each step you take and any issues encountered.
"""
    
    async def _execute_nova_act_automation(
        self,
        page: Page,
        context: Dict[str, Any],
        instructions: str,
        initial_screenshot: bytes,
        max_steps: int,
        timeout_seconds: int,
        request_id: str
    ) -> NovaActResult:
        """Execute the actual Nova Act automation"""
        
        steps_taken = []
        screenshots = []
        current_step = 1
        
        try:
            # Encode initial screenshot
            initial_screenshot_b64 = base64.b64encode(initial_screenshot).decode('utf-8')
            screenshots.append(initial_screenshot_b64)
            
            # Prepare Nova Act request
            nova_request = {
                "modelId": self.model_id,
                "contentType": "application/json",
                "accept": "application/json",
                "body": json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": instructions
                                },
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": initial_screenshot_b64
                                    }
                                }
                            ]
                        }
                    ],
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "temperature": 0.1,
                    "tool_use": {
                        "enabled": True,
                        "tools": [
                            {
                                "name": "browser_action",
                                "description": "Perform browser actions like clicking, typing, scrolling",
                                "input_schema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {
                                            "type": "string",
                                            "enum": ["click", "type", "scroll", "select", "submit", "wait", "screenshot"]
                                        },
                                        "selector": {"type": "string"},
                                        "text": {"type": "string"},
                                        "coordinates": {"type": "array"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["action", "description"]
                                }
                            }
                        ]
                    }
                })
            }
            
            # Execute Nova Act step by step
            while current_step <= max_steps:
                step_start_time = datetime.now()
                
                # Take screenshot before action
                screenshot_before = await page.screenshot(full_page=True)
                screenshot_before_b64 = base64.b64encode(screenshot_before).decode('utf-8')
                
                # Call Nova Act
                response = await self._call_nova_act_api(nova_request)
                
                if not response or "error" in response:
                    error_msg = response.get("error", "Unknown Nova Act API error")
                    steps_taken.append(NovaActStep(
                        step_number=current_step,
                        action="api_call",
                        description="Nova Act API call failed",
                        screenshot_before=screenshot_before_b64,
                        screenshot_after=None,
                        success=False,
                        error=error_msg,
                        metadata={"response": response}
                    ))
                    break
                
                # Parse Nova Act response
                action_result = await self._execute_nova_action(page, response)
                
                # Take screenshot after action
                screenshot_after = await page.screenshot(full_page=True)
                screenshot_after_b64 = base64.b64encode(screenshot_after).decode('utf-8')
                screenshots.append(screenshot_after_b64)
                
                # Record step
                step = NovaActStep(
                    step_number=current_step,
                    action=action_result.get("action", "unknown"),
                    description=action_result.get("description", "Nova Act action"),
                    screenshot_before=screenshot_before_b64,
                    screenshot_after=screenshot_after_b64,
                    success=action_result.get("success", False),
                    error=action_result.get("error"),
                    metadata=action_result.get("metadata", {})
                )
                steps_taken.append(step)
                
                # Check if task is complete
                if action_result.get("task_complete", False):
                    break
                
                # Check for timeout
                if (datetime.now() - step_start_time).total_seconds() > timeout_seconds:
                    break
                
                current_step += 1
            
            # Analyze final state
            final_analysis = await self._analyze_final_state(page, steps_taken)
            
            return NovaActResult(
                success=final_analysis["success"],
                steps_taken=steps_taken,
                final_state=final_analysis["state"],
                errors=final_analysis["errors"],
                screenshots=screenshots,
                duration_seconds=0,  # Will be set by caller
                form_submitted=final_analysis["form_submitted"],
                confirmation_detected=final_analysis["confirmation_detected"],
                metadata=final_analysis["metadata"]
            )
            
        except Exception as e:
            self.logger.error("Nova Act automation error", {
                "operation": "nova_act_automation_error",
                "request_id": request_id,
                "step": current_step,
                "error": str(e)
            })
            
            return NovaActResult(
                success=False,
                steps_taken=steps_taken,
                final_state="error",
                errors=[str(e)],
                screenshots=screenshots,
                duration_seconds=0,
                form_submitted=False,
                confirmation_detected=False,
                metadata={"error": str(e)}
            )
    
    async def _call_nova_act_api(self, request: Dict) -> Dict:
        """Call the Nova Act API"""
        
        try:
            response = self.bedrock_client.invoke_model(
                modelId=request["modelId"],
                contentType=request["contentType"],
                accept=request["accept"],
                body=request["body"]
            )
            
            response_body = json.loads(response['body'].read())
            return response_body
            
        except ClientError as e:
            self.logger.error("AWS Bedrock API error", {
                "operation": "bedrock_api_error",
                "error_code": e.response['Error']['Code'],
                "error_message": e.response['Error']['Message']
            })
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
            
        except Exception as e:
            self.logger.error("Nova Act API call failed", {
                "operation": "nova_api_call_error",
                "error": str(e)
            })
            return {"error": f"API call failed: {str(e)}"}
    
    async def _execute_nova_action(self, page: Page, nova_response: Dict) -> Dict:
        """Execute the action recommended by Nova Act"""
        
        try:
            # Parse Nova Act response to extract action
            content = nova_response.get("content", [])
            
            for item in content:
                if item.get("type") == "tool_use":
                    tool_input = item.get("input", {})
                    action = tool_input.get("action")
                    
                    if action == "click":
                        return await self._handle_click_action(page, tool_input)
                    elif action == "type":
                        return await self._handle_type_action(page, tool_input)
                    elif action == "select":
                        return await self._handle_select_action(page, tool_input)
                    elif action == "submit":
                        return await self._handle_submit_action(page, tool_input)
                    elif action == "scroll":
                        return await self._handle_scroll_action(page, tool_input)
                    elif action == "wait":
                        return await self._handle_wait_action(page, tool_input)
                    elif action == "screenshot":
                        return await self._handle_screenshot_action(page, tool_input)
            
            # If no specific action found, treat as analysis/observation
            return {
                "action": "analysis",
                "description": "Nova Act analyzed the page",
                "success": True,
                "metadata": {"response": nova_response}
            }
            
        except Exception as e:
            return {
                "action": "error",
                "description": f"Failed to execute Nova action: {str(e)}",
                "success": False,
                "error": str(e),
                "metadata": {"nova_response": nova_response}
            }
    
    async def _handle_click_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle click action from Nova Act"""
        
        try:
            selector = tool_input.get("selector")
            coordinates = tool_input.get("coordinates")
            description = tool_input.get("description", "Click action")
            
            if selector:
                element = page.locator(selector)
                if await element.count() > 0:
                    await element.first.click()
                    return {
                        "action": "click",
                        "description": f"Clicked element: {selector}",
                        "success": True,
                        "metadata": {"selector": selector}
                    }
                else:
                    return {
                        "action": "click",
                        "description": f"Element not found: {selector}",
                        "success": False,
                        "error": "Element not found"
                    }
            elif coordinates and len(coordinates) >= 2:
                await page.mouse.click(coordinates[0], coordinates[1])
                return {
                    "action": "click",
                    "description": f"Clicked at coordinates: {coordinates}",
                    "success": True,
                    "metadata": {"coordinates": coordinates}
                }
            else:
                return {
                    "action": "click",
                    "description": "Invalid click parameters",
                    "success": False,
                    "error": "No valid selector or coordinates provided"
                }
                
        except Exception as e:
            return {
                "action": "click",
                "description": f"Click failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_type_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle type action from Nova Act"""
        
        try:
            selector = tool_input.get("selector")
            text = tool_input.get("text", "")
            description = tool_input.get("description", "Type action")
            
            if selector and text:
                element = page.locator(selector)
                if await element.count() > 0:
                    await element.first.fill(text)
                    return {
                        "action": "type",
                        "description": f"Typed '{text}' into {selector}",
                        "success": True,
                        "metadata": {"selector": selector, "text": text}
                    }
                else:
                    return {
                        "action": "type",
                        "description": f"Element not found: {selector}",
                        "success": False,
                        "error": "Element not found"
                    }
            else:
                return {
                    "action": "type",
                    "description": "Invalid type parameters",
                    "success": False,
                    "error": "Missing selector or text"
                }
                
        except Exception as e:
            return {
                "action": "type",
                "description": f"Type failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_select_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle select dropdown action from Nova Act"""
        
        try:
            selector = tool_input.get("selector")
            text = tool_input.get("text", "")
            description = tool_input.get("description", "Select action")
            
            if selector and text:
                element = page.locator(selector)
                if await element.count() > 0:
                    await element.first.select_option(label=text)
                    return {
                        "action": "select",
                        "description": f"Selected '{text}' from {selector}",
                        "success": True,
                        "metadata": {"selector": selector, "option": text}
                    }
                else:
                    return {
                        "action": "select",
                        "description": f"Dropdown not found: {selector}",
                        "success": False,
                        "error": "Dropdown element not found"
                    }
            else:
                return {
                    "action": "select",
                    "description": "Invalid select parameters",
                    "success": False,
                    "error": "Missing selector or option text"
                }
                
        except Exception as e:
            return {
                "action": "select",
                "description": f"Select failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_submit_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle form submit action from Nova Act"""
        
        try:
            selector = tool_input.get("selector", "button[type='submit']")
            description = tool_input.get("description", "Submit form")
            
            element = page.locator(selector)
            if await element.count() > 0:
                await element.first.click()
                
                # Wait for potential page navigation or response
                await page.wait_for_timeout(3000)
                
                return {
                    "action": "submit",
                    "description": f"Submitted form using {selector}",
                    "success": True,
                    "metadata": {"selector": selector},
                    "task_complete": True  # Mark task as potentially complete
                }
            else:
                return {
                    "action": "submit",
                    "description": f"Submit button not found: {selector}",
                    "success": False,
                    "error": "Submit button not found"
                }
                
        except Exception as e:
            return {
                "action": "submit",
                "description": f"Submit failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_scroll_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle scroll action from Nova Act"""
        
        try:
            coordinates = tool_input.get("coordinates", [0, 500])
            description = tool_input.get("description", "Scroll page")
            
            await page.mouse.wheel(coordinates[0], coordinates[1])
            
            return {
                "action": "scroll",
                "description": f"Scrolled by {coordinates}",
                "success": True,
                "metadata": {"scroll_delta": coordinates}
            }
            
        except Exception as e:
            return {
                "action": "scroll",
                "description": f"Scroll failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_wait_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle wait action from Nova Act"""
        
        try:
            wait_time = tool_input.get("time", 2000)  # Default 2 seconds
            description = tool_input.get("description", "Wait")
            
            await page.wait_for_timeout(wait_time)
            
            return {
                "action": "wait",
                "description": f"Waited {wait_time}ms",
                "success": True,
                "metadata": {"wait_time": wait_time}
            }
            
        except Exception as e:
            return {
                "action": "wait",
                "description": f"Wait failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_screenshot_action(self, page: Page, tool_input: Dict) -> Dict:
        """Handle screenshot action from Nova Act"""
        
        try:
            description = tool_input.get("description", "Take screenshot")
            
            screenshot = await page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            return {
                "action": "screenshot",
                "description": "Screenshot captured",
                "success": True,
                "metadata": {"screenshot": screenshot_b64}
            }
            
        except Exception as e:
            return {
                "action": "screenshot",
                "description": f"Screenshot failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_final_state(self, page: Page, steps: List[NovaActStep]) -> Dict:
        """Analyze the final state to determine success"""
        
        try:
            # Check current page URL and content
            current_url = page.url
            page_content = await page.content()
            page_title = await page.title()
            
            # Look for success indicators
            success_indicators = [
                "thank you", "success", "submitted", "received", 
                "we'll contact", "confirmation", "complete"
            ]
            
            error_indicators = [
                "error", "failed", "invalid", "required field",
                "please fill", "missing information"
            ]
            
            content_lower = page_content.lower()
            title_lower = page_title.lower()
            
            # Check for success indicators
            confirmation_detected = any(
                indicator in content_lower or indicator in title_lower 
                for indicator in success_indicators
            )
            
            # Check for error indicators  
            errors_detected = any(
                indicator in content_lower or indicator in title_lower
                for indicator in error_indicators
            )
            
            # Check if form was submitted (based on steps)
            form_submitted = any(
                step.action == "submit" and step.success 
                for step in steps
            )
            
            # Determine overall success
            success = form_submitted and confirmation_detected and not errors_detected
            
            return {
                "success": success,
                "state": "completed" if success else "failed",
                "form_submitted": form_submitted,
                "confirmation_detected": confirmation_detected,
                "errors": ["Error indicators found in page"] if errors_detected else [],
                "metadata": {
                    "final_url": current_url,
                    "page_title": page_title,
                    "success_indicators_found": confirmation_detected,
                    "error_indicators_found": errors_detected
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "state": "analysis_failed",
                "form_submitted": False,
                "confirmation_detected": False,
                "errors": [f"Final state analysis failed: {str(e)}"],
                "metadata": {"error": str(e)}
            }