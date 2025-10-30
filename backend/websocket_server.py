"""
WebSocket Server for Real-Time Dealership Contact Automation

Provides real-time updates to the frontend UI including:
- Contact progress updates
- Success/failure notifications
- Screenshot streaming
- CAPTCHA detection alerts
- Form detection failures
"""

import asyncio
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
sys.path.append('..')

from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler
from src.automation.forms.enhanced_form_submitter import EnhancedFormSubmitter
from src.automation.forms.early_captcha_detector import EarlyCaptchaDetector
from src.automation.navigation.contact_page_finder import ContactPageFinder
from src.services.captcha_tracker import CaptchaTracker
from src.services.contact_url_cache import ContactURLCache
from src.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Dealership Contact Automation API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve screenshots directory
screenshots_dir = Path("../screenshots")
screenshots_dir.mkdir(exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=str(screenshots_dir)), name="screenshots")


class ContactRequest(BaseModel):
    """Request to contact a dealership"""
    dealer_name: str
    website: str
    city: str
    state: str
    customer_info: Dict[str, str]  # firstName, lastName, email, phone, zipcode, message


class WebSocketManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to websocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = WebSocketManager()


def validate_and_normalize_url(url: str) -> Optional[str]:
    """
    Validate and normalize dealer website URL.

    Returns normalized URL or None if invalid.
    """
    from urllib.parse import urlparse

    if not url or not isinstance(url, str):
        return None

    url = url.strip()

    # Add https:// if no protocol
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    try:
        parsed = urlparse(url)

        # Only allow http/https
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Invalid URL scheme: {parsed.scheme}")
            return None

        # Must have domain
        if not parsed.netloc:
            logger.warning(f"URL missing domain: {url}")
            return None

        return url
    except Exception as e:
        logger.error(f"URL parsing error: {e}")
        return None


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Removes:
    - Path separators (/, \)
    - Parent directory references (..)
    - Non-alphanumeric characters (except spaces, hyphens, underscores)
    """
    import re

    # Remove any path separators
    name = name.replace('/', '_').replace('\\', '_')
    # Remove any parent directory references
    name = name.replace('..', '_')
    # Keep only alphanumeric, spaces, hyphens, underscores
    name = re.sub(r'[^a-zA-Z0-9\s\-_]', '_', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Trim to max length
    return name[:max_length].strip('_')


def generate_screenshot_filename(dealer_name: str, suffix: str) -> str:
    """
    Generate unique screenshot filename with timestamp to prevent collisions.

    Args:
        dealer_name: Name of the dealership
        suffix: Type of screenshot (captcha, filled, success, failed)

    Returns:
        Filename in format: DealerName_suffix_YYYYMMDD_HHMMSS.png
    """
    safe_name = sanitize_filename(dealer_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe_name}_{suffix}_{timestamp}.png"


def create_event(event_type: str, data: Dict) -> Dict:
    """Create standardized event message"""
    return {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }


async def ensure_screenshot_dir(screenshots_dir: Path) -> bool:
    """
    Ensure screenshots directory exists and is writable.

    Returns True if directory is ready, False otherwise.
    """
    try:
        # If path exists, verify it's actually a directory
        if screenshots_dir.exists() and not screenshots_dir.is_dir():
            logger.error(f"Screenshots path exists but is not a directory: {screenshots_dir}")
            return False

        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Verify it's writable by creating and deleting a test file
        test_file = screenshots_dir / ".write_test"
        test_file.touch()
        test_file.unlink()

        return True
    except Exception as e:
        logger.error(f"Cannot create/write to screenshots directory: {e}")
        return False


async def cleanup_old_screenshots(screenshots_dir: Path, max_age_hours: int = 24):
    """
    Background task to delete screenshots older than max_age_hours.

    Runs continuously, checking every hour.
    """
    import time

    logger.info(f"Screenshot cleanup task started (max age: {max_age_hours} hours)")

    while True:
        try:
            now = time.time()
            cleaned_count = 0

            for screenshot in screenshots_dir.glob("*.png"):
                try:
                    age_hours = (now - screenshot.stat().st_mtime) / 3600

                    if age_hours > max_age_hours:
                        screenshot.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old screenshot: {screenshot.name} (age: {age_hours:.1f}h)")
                except Exception as e:
                    logger.error(f"Error cleaning screenshot {screenshot.name}: {e}")

            if cleaned_count > 0:
                logger.info(f"Screenshot cleanup: removed {cleaned_count} old screenshots")

        except Exception as e:
            logger.error(f"Screenshot cleanup error: {e}")

        # Run every hour
        await asyncio.sleep(3600)


async def take_screenshot_safely(page, screenshot_path: Path, dealer_name: str) -> bool:
    """
    Take screenshot with error handling and page state checking.

    Returns True if successful, False otherwise.
    """
    try:
        # Check if page is still open before attempting screenshot
        if page.is_closed():
            logger.warning(f"Page already closed, skipping screenshot for {dealer_name}")
            return False

        await page.screenshot(path=str(screenshot_path), full_page=True)
        logger.debug(f"Screenshot saved: {screenshot_path.name}")
        return True
    except Exception as e:
        logger.error(f"Screenshot failed for {dealer_name}: {e}")
        return False


async def encode_screenshot(screenshot_path: Path) -> Optional[str]:
    """
    Encode screenshot as base64 for transmission using async I/O.

    This prevents blocking the event loop during file reading.
    """
    try:
        if not screenshot_path.exists():
            return None

        # Use asyncio to read file without blocking
        import aiofiles

        async with aiofiles.open(screenshot_path, 'rb') as f:
            image_bytes = await f.read()
            return base64.b64encode(image_bytes).decode('utf-8')
    except ImportError:
        # Fallback to synchronous if aiofiles not installed
        logger.warning("aiofiles not installed, using synchronous file I/O")
        try:
            with open(screenshot_path, 'rb') as f:
                image_bytes = f.read()
                return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding screenshot: {e}")
            return None
    except Exception as e:
        logger.error(f"Error encoding screenshot: {e}")
        return None


async def contact_dealership_with_updates(
    dealership: Dict,
    customer_info: Dict,
    websocket: WebSocket
) -> Dict:
    """
    Contact a single dealership with real-time WebSocket updates.

    Events sent:
    - contact_started: Initial notification
    - navigation_started: Navigating to website
    - contact_page_found: Found contact page
    - captcha_detected: CAPTCHA blocking automation
    - form_not_found: Could not find contact form
    - form_detected: Successfully found form
    - filling_form: Starting to fill fields
    - form_filled: All fields filled
    - submitting: Attempting submission
    - contact_success: Successfully submitted
    - contact_failed: Submission failed
    - screenshot: Screenshot available
    """

    result = {
        "dealer_name": dealership["dealer_name"],
        "website": dealership["website"],
        "success": False,
        "reason": None,
        "contact_url": None,
        "screenshots": [],
        "captcha_type": None,
        "error": None
    }

    playwright_instance = None
    browser = None
    context = None
    page = None
    browser_manager = None

    try:
        # Validate and normalize website URL
        website_url = validate_and_normalize_url(dealership.get("website"))
        if not website_url:
            await manager.send_message(create_event("contact_error", {
                "dealer_name": dealership["dealer_name"],
                "error": f"Invalid website URL: {dealership.get('website')}"
            }), websocket)
            result["error"] = "Invalid website URL"
            result["reason"] = "invalid_url"
            # Send contact_complete before returning
            await manager.send_message(create_event("contact_complete", {
                "result": result
            }), websocket)
            return result

        # Update dealership with normalized URL
        dealership["website"] = website_url

        # Ensure screenshots directory exists and is writable
        if not await ensure_screenshot_dir(screenshots_dir):
            await manager.send_message(create_event("contact_error", {
                "dealer_name": dealership["dealer_name"],
                "error": "Screenshots directory not accessible"
            }), websocket)
            result["error"] = "Screenshots directory not accessible"
            result["reason"] = "screenshot_dir_error"
            # Send contact_complete before returning
            await manager.send_message(create_event("contact_complete", {
                "result": result
            }), websocket)
            return result

        # Event: Contact started
        await manager.send_message(create_event("contact_started", {
            "dealer_name": dealership["dealer_name"],
            "website": website_url
        }), websocket)

        # Create browser
        try:
            playwright_instance, browser, context, page, browser_manager = await asyncio.wait_for(
                create_enhanced_stealth_session(headless=False),
                timeout=30  # 30 seconds to create browser
            )
        except asyncio.TimeoutError:
            await manager.send_message(create_event("contact_error", {
                "dealer_name": dealership["dealer_name"],
                "error": "Browser creation timeout"
            }), websocket)
            result["error"] = "Browser creation timeout"
            result["reason"] = "timeout"
            await manager.send_message(create_event("contact_complete", {"result": result}), websocket)
            return result

        # Event: Navigation started
        await manager.send_message(create_event("navigation_started", {
            "dealer_name": dealership["dealer_name"],
            "url": website_url
        }), websocket)

        # Initialize services
        contact_finder = ContactPageFinder(ContactURLCache())
        captcha_tracker = CaptchaTracker()

        # Find contact page
        async def validate_contact_form(page_obj):
            detector = EnhancedFormDetector()
            form_result = await detector.detect_contact_form(page_obj)

            if not form_result.success:
                return (False, None)

            field_count = len(form_result.fields)
            if field_count < 4:
                return (False, None)

            return (True, {
                'field_count': field_count,
                'field_types': list(form_result.fields.keys()),
                'has_submit': bool(form_result.submit_button),
                'confidence': form_result.confidence_score
            })

        try:
            contact_url, form_data = await asyncio.wait_for(
                contact_finder.navigate_to_contact_page(
                    page=page,
                    website_url=dealership['website'],
                    form_validator=validate_contact_form
                ),
                timeout=60  # 60 seconds max for navigation and form detection
            )
        except asyncio.TimeoutError:
            await manager.send_message(create_event("contact_error", {
                "dealer_name": dealership["dealer_name"],
                "error": "Navigation timeout - site too slow or unresponsive"
            }), websocket)
            result["error"] = "Navigation timeout"
            result["reason"] = "timeout"
            await manager.send_message(create_event("contact_complete", {"result": result}), websocket)
            return result

        if not contact_url:
            # Event: Form not found
            await manager.send_message(create_event("form_not_found", {
                "dealer_name": dealership["dealer_name"],
                "website": dealership["website"],
                "reason": "No contact page with valid form found"
            }), websocket)

            result["reason"] = "form_not_found"
            result["error"] = "No contact page with valid form found"
            # Send contact_complete before returning
            await manager.send_message(create_event("contact_complete", {
                "result": result
            }), websocket)
            return result

        result["contact_url"] = contact_url

        # Event: Contact page found
        await manager.send_message(create_event("contact_page_found", {
            "dealer_name": dealership["dealer_name"],
            "contact_url": contact_url,
            "form_field_count": form_data.get('field_count', 0)
        }), websocket)

        await asyncio.sleep(2)

        # EARLY CAPTCHA DETECTION
        captcha_detector = EarlyCaptchaDetector()
        captcha_result = await captcha_detector.wait_and_detect(page, wait_seconds=2.0)

        if captcha_result["has_captcha"]:
            # Take screenshot of CAPTCHA
            screenshot_filename = generate_screenshot_filename(dealership['dealer_name'], "captcha")
            screenshot_path = screenshots_dir / screenshot_filename

            try:
                await page.screenshot(path=str(screenshot_path), full_page=True)
                # Encode and send screenshot
                screenshot_base64 = await encode_screenshot(screenshot_path)
            except Exception as screenshot_error:
                logger.error(f"Screenshot failed for {dealership['dealer_name']}: {screenshot_error}")
                screenshot_base64 = None
                # Continue without screenshot

            # Event: CAPTCHA detected
            await manager.send_message(create_event("captcha_detected", {
                "dealer_name": dealership["dealer_name"],
                "contact_url": contact_url,
                "captcha_type": captcha_result["captcha_type"],
                "selector": captcha_result["selector"],
                "screenshot": screenshot_base64,
                "screenshot_url": f"/screenshots/{screenshot_path.name}"
            }), websocket)

            result["reason"] = "captcha_detected"
            result["captcha_type"] = captcha_result["captcha_type"]
            result["screenshots"].append(str(screenshot_path.name))

            # Track for manual follow-up
            captcha_tracker.add_site(
                dealer_name=dealership["dealer_name"],
                website=dealership["website"],
                contact_url=contact_url,
                reason="CAPTCHA",
                captcha_type=captcha_result["captcha_type"],
                notes=f"Early detection: {captcha_result['selector']}"
            )

            # Send contact_complete before returning
            await manager.send_message(create_event("contact_complete", {
                "result": result
            }), websocket)

            return result

        # Event: Form detected (no CAPTCHA)
        await manager.send_message(create_event("form_detected", {
            "dealer_name": dealership["dealer_name"],
            "field_count": form_data.get('field_count', 0),
            "confidence": form_data.get('confidence', 0.0)
        }), websocket)

        # Re-detect form for detailed field information
        form_detector = EnhancedFormDetector()
        form_result = await form_detector.detect_contact_form(page)

        if not form_result.success:
            result["reason"] = "form_detection_failed"
            result["error"] = "Form detection failed on re-check"
            # Send contact_complete before returning
            await manager.send_message(create_event("contact_complete", {
                "result": result
            }), websocket)
            return result

        # Event: Filling form
        await manager.send_message(create_event("filling_form", {
            "dealer_name": dealership["dealer_name"],
            "field_count": len(form_result.fields)
        }), websocket)

        # Initialize handlers
        complex_handler = ComplexFieldHandler()

        # Handle complex fields
        split_phone = await complex_handler.detect_split_phone_field(page)
        if split_phone:
            await complex_handler.fill_split_phone_field(split_phone, customer_info["phone"])

        complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
        if complex_name:
            await complex_handler.fill_complex_name_field(
                complex_name, customer_info["firstName"], customer_info["lastName"]
            )

        gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)
        if gravity_zip:
            await gravity_zip.fill(customer_info["zipcode"])

        # Fill standard fields
        field_mapping = {
            "first_name": customer_info.get("firstName"),
            "last_name": customer_info.get("lastName"),
            "email": customer_info.get("email"),
            "phone": customer_info.get("phone"),
            "zip_code": customer_info.get("zipcode"),
            "message": customer_info.get("message")
        }

        for field_type, field_info in form_result.fields.items():
            # Skip if already handled by complex handlers
            if field_type == "phone" and split_phone:
                continue
            if field_type in ["first_name", "last_name"] and complex_name:
                continue
            if field_type in ["zip", "zip_code"] and gravity_zip:
                continue

            value = field_mapping.get(field_type)
            if not value:
                continue

            try:
                await field_info.element.fill(value)
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.warning(f"Failed to fill {field_type}: {str(e)}")

        # Take screenshot of filled form
        filled_screenshot_filename = generate_screenshot_filename(dealership['dealer_name'], "filled")
        filled_screenshot_path = screenshots_dir / filled_screenshot_filename
        await page.screenshot(path=str(filled_screenshot_path), full_page=True)
        result["screenshots"].append(str(filled_screenshot_path.name))

        # Event: Form filled
        filled_screenshot_base64 = await encode_screenshot(filled_screenshot_path)
        await manager.send_message(create_event("form_filled", {
            "dealer_name": dealership["dealer_name"],
            "screenshot": filled_screenshot_base64,
            "screenshot_url": f"/screenshots/{filled_screenshot_path.name}"
        }), websocket)

        # Event: Submitting
        await manager.send_message(create_event("submitting", {
            "dealer_name": dealership["dealer_name"]
        }), websocket)

        # Submit form with timeout
        submitter = EnhancedFormSubmitter()
        try:
            submission_result = await asyncio.wait_for(
                submitter.submit_form(page, form_result.form_element),
                timeout=30  # 30 seconds max for submission
            )
        except asyncio.TimeoutError:
            await manager.send_message(create_event("contact_error", {
                "dealer_name": dealership["dealer_name"],
                "error": "Form submission timeout"
            }), websocket)
            result["error"] = "Form submission timeout"
            result["reason"] = "timeout"
            await manager.send_message(create_event("contact_complete", {"result": result}), websocket)
            return result

        if submission_result.success:
            # Take success screenshot
            success_screenshot_filename = generate_screenshot_filename(dealership['dealer_name'], "success")
            success_screenshot_path = screenshots_dir / success_screenshot_filename
            await page.screenshot(path=str(success_screenshot_path), full_page=True)
            result["screenshots"].append(str(success_screenshot_path.name))

            success_screenshot_base64 = await encode_screenshot(success_screenshot_path)

            # Event: Contact success
            await manager.send_message(create_event("contact_success", {
                "dealer_name": dealership["dealer_name"],
                "contact_url": contact_url,
                "submission_method": submission_result.method,
                "verification": submission_result.verification,
                "screenshot": success_screenshot_base64,
                "screenshot_url": f"/screenshots/{success_screenshot_path.name}"
            }), websocket)

            result["success"] = True
            result["reason"] = "success"
        else:
            # Take failure screenshot
            failure_screenshot_filename = generate_screenshot_filename(dealership['dealer_name'], "failed")
            failure_screenshot_path = screenshots_dir / failure_screenshot_filename
            await page.screenshot(path=str(failure_screenshot_path), full_page=True)
            result["screenshots"].append(str(failure_screenshot_path.name))

            failure_screenshot_base64 = await encode_screenshot(failure_screenshot_path)

            # Event: Contact failed
            await manager.send_message(create_event("contact_failed", {
                "dealer_name": dealership["dealer_name"],
                "contact_url": contact_url,
                "blocker": submission_result.blocker,
                "error": submission_result.error,
                "screenshot": failure_screenshot_base64,
                "screenshot_url": f"/screenshots/{failure_screenshot_path.name}"
            }), websocket)

            result["success"] = False
            result["reason"] = submission_result.blocker or "submission_failed"
            result["error"] = submission_result.error

        await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"Contact automation error: {str(e)}")

        # Event: Error
        await manager.send_message(create_event("contact_error", {
            "dealer_name": dealership["dealer_name"],
            "error": str(e)
        }), websocket)

        result["error"] = str(e)
        result["reason"] = "exception"

        # NOTE: Don't send contact_complete here - let WebSocket handler send it
        # This prevents double-sending when exception is caught

    finally:
        # Wait for any pending operations to complete
        try:
            await asyncio.sleep(0.5)
        except:
            pass

        # Cleanup browser resources in correct order with timeouts
        try:
            if page and not page.is_closed():
                await asyncio.wait_for(page.close(), timeout=5)
                logger.debug("Page closed successfully")
        except asyncio.TimeoutError:
            logger.error("Page close timeout (5s)")
        except Exception as e:
            logger.error(f"Error closing page: {e}")

        try:
            if context and hasattr(context, 'close'):
                await asyncio.wait_for(context.close(), timeout=5)
                logger.debug("Context closed successfully")
        except asyncio.TimeoutError:
            logger.error("Context close timeout (5s)")
        except Exception as e:
            logger.error(f"Error closing context: {e}")

        try:
            if browser:
                await asyncio.wait_for(browser.close(), timeout=10)
                logger.debug("Browser closed successfully")
        except asyncio.TimeoutError:
            logger.error("Browser close timeout (10s)")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

        try:
            if playwright_instance:
                await asyncio.wait_for(playwright_instance.stop(), timeout=5)
                logger.debug("Playwright stopped successfully")
        except asyncio.TimeoutError:
            logger.error("Playwright stop timeout (5s)")
        except Exception as e:
            logger.error(f"Error stopping playwright: {e}")

    return result


@app.websocket("/ws/contact")
async def websocket_contact_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time contact automation"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive contact request from frontend with timeout
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=300  # 5 minutes timeout
                )
            except asyncio.TimeoutError:
                # Send ping to check if client still alive
                try:
                    await manager.send_message(create_event("ping", {}), websocket)
                    continue
                except:
                    # Client is dead, close connection
                    logger.info("Client not responding to ping, closing connection")
                    break

            message_type = data.get("type")

            if message_type == "contact_dealer":
                dealership = data.get("dealership")
                customer_info = data.get("customer_info")

                # Validate required fields
                if not dealership or not isinstance(dealership, dict):
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": "Unknown",
                        "error": "Invalid dealership data"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": "Unknown",
                            "success": False,
                            "reason": "validation_error",
                            "error": "Invalid dealership data"
                        }
                    }), websocket)
                    continue

                if not customer_info or not isinstance(customer_info, dict):
                    dealer_name = dealership.get("dealer_name", "Unknown") if dealership else "Unknown"
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": "Invalid customer info data"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "validation_error",
                            "error": "Invalid customer info data"
                        }
                    }), websocket)
                    continue

                # Check required dealership fields
                required_dealer_fields = ["dealer_name", "website"]
                missing_dealer = [f for f in required_dealer_fields if not dealership.get(f)]
                if missing_dealer:
                    dealer_name = dealership.get("dealer_name", "Unknown")
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": f"Missing required dealership fields: {', '.join(missing_dealer)}"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "validation_error",
                            "error": f"Missing fields: {', '.join(missing_dealer)}"
                        }
                    }), websocket)
                    continue

                # Check required customer fields
                required_customer_fields = ["firstName", "lastName", "email", "phone", "message"]
                missing_customer = [
                    f for f in required_customer_fields
                    if not customer_info.get(f) or not str(customer_info.get(f)).strip()
                ]
                if missing_customer:
                    dealer_name = dealership.get("dealer_name", "Unknown")
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": f"Missing or empty customer fields: {', '.join(missing_customer)}"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "validation_error",
                            "error": f"Missing customer fields: {', '.join(missing_customer)}"
                        }
                    }), websocket)
                    continue

                # Validate email format
                email = customer_info.get("email", "")
                import re
                email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if not re.match(email_regex, email):
                    dealer_name = dealership.get("dealer_name", "Unknown")
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": f"Invalid email format: {email}"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "validation_error",
                            "error": f"Invalid email: {email}"
                        }
                    }), websocket)
                    continue

                # Validate phone number (should be 10 digits for US)
                phone = customer_info.get("phone", "")
                phone_digits = re.sub(r'\D', '', phone)
                if len(phone_digits) != 10:
                    dealer_name = dealership.get("dealer_name", "Unknown")
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": f"Phone must be 10 digits (US format), got: {phone}"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "validation_error",
                            "error": f"Invalid phone: {phone}"
                        }
                    }), websocket)
                    continue

                # Validate zipcode if provided
                zipcode = customer_info.get("zipcode", "")
                if zipcode:
                    zipcode_digits = re.sub(r'\D', '', zipcode)
                    if len(zipcode_digits) != 5 and len(zipcode_digits) != 9:
                        dealer_name = dealership.get("dealer_name", "Unknown")
                        await manager.send_message(create_event("contact_error", {
                            "dealer_name": dealer_name,
                            "error": f"Zipcode must be 5 or 9 digits, got: {zipcode}"
                        }), websocket)
                        await manager.send_message(create_event("contact_complete", {
                            "result": {
                                "dealer_name": dealer_name,
                                "success": False,
                                "reason": "validation_error",
                                "error": f"Invalid zipcode: {zipcode}"
                            }
                        }), websocket)
                        continue

                logger.info(f"Received contact request for: {dealership['dealer_name']}")

                # Run contact automation with real-time updates (wrapped in try-catch)
                try:
                    result = await contact_dealership_with_updates(
                        dealership=dealership,
                        customer_info=customer_info,
                        websocket=websocket
                    )

                    # Send final result
                    await manager.send_message(create_event("contact_complete", {
                        "result": result
                    }), websocket)
                except Exception as e:
                    # Critical: Catch any unhandled exceptions from automation
                    logger.error(f"Unhandled error in contact automation: {e}", exc_info=True)
                    dealer_name = dealership.get("dealer_name", "Unknown")
                    await manager.send_message(create_event("contact_error", {
                        "dealer_name": dealer_name,
                        "error": f"Critical automation error: {str(e)}"
                    }), websocket)
                    await manager.send_message(create_event("contact_complete", {
                        "result": {
                            "dealer_name": dealer_name,
                            "success": False,
                            "reason": "critical_error",
                            "error": str(e)
                        }
                    }), websocket)

            elif message_type == "ping":
                # Keep-alive ping
                await manager.send_message(create_event("pong", {}), websocket)

            elif message_type == "cancel_contact":
                # TODO: Implement contact cancellation
                logger.warning("Contact cancellation requested but not yet implemented")
                await manager.send_message(create_event("error", {
                    "error": "Cancellation not yet implemented"
                }), websocket)

            else:
                # Unknown message type
                logger.warning(f"Unknown message type received: {message_type}")
                await manager.send_message(create_event("error", {
                    "error": f"Unknown message type: {message_type}"
                }), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup"""
    logger.info("Starting background tasks...")

    # Start screenshot cleanup task
    asyncio.create_task(cleanup_old_screenshots(screenshots_dir, max_age_hours=24))

    logger.info("Background tasks started")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Dealership Contact Automation API",
        "active_connections": len(manager.active_connections)
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "websocket_connections": len(manager.active_connections),
        "screenshots_dir": str(screenshots_dir),
        "screenshots_count": len(list(screenshots_dir.glob("*.png")))
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting WebSocket server...")
    logger.info(f"Screenshots directory: {screenshots_dir.absolute()}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
