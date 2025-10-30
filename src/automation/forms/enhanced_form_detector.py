"""
Enhanced form detection with JavaScript-heavy page handling and iframe support.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import Page, Locator

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EnhancedFormField:
    """Enhanced form field representation"""
    element: Locator
    field_type: str
    selector: str
    confidence: float
    is_in_iframe: bool = False


@dataclass  
class EnhancedFormResult:
    """Enhanced form detection result"""
    success: bool
    form_element: Optional[Locator]
    fields: Dict[str, EnhancedFormField]
    submit_button: Optional[Locator]
    confidence_score: float
    is_in_iframe: bool = False
    iframe_src: Optional[str] = None


class EnhancedFormDetector:
    """Enhanced form detector with JavaScript and iframe support"""
    
    def __init__(self):
        self.logger = logger
        
        # Enhanced field selectors for modern dealership websites
        self.field_selectors = {
            "first_name": [
                "input[name*='first' i]",
                "input[id*='first' i]", 
                "input[placeholder*='first' i]",
                "input[name*='fname' i]",
                "input[id*='fname' i]",
                "input[data-field*='first' i]",
                "input[class*='first' i]",
                "#firstName", "#firstname", "#fname", "#first_name",
                "input[name='FirstName']", "input[name='first_name']",
                "[name='lead_first_name']", "[name='customer_first_name']"
            ],
            "last_name": [
                "input[name*='last' i]",
                "input[id*='last' i]",
                "input[placeholder*='last' i]",
                "input[name*='lname' i]", 
                "input[id*='lname' i]",
                "input[data-field*='last' i]",
                "input[class*='last' i]",
                "#lastName", "#lastname", "#lname", "#last_name",
                "input[name='LastName']", "input[name='last_name']",
                "[name='lead_last_name']", "[name='customer_last_name']"
            ],
            "name": [
                "input[name*='name' i]",
                "input[id*='name' i]",
                "input[placeholder*='name' i]",
                "input[name='Name']", "input[name='name']",
                "input[data-field*='name' i]",
                "#name", "#fullname", "#full_name",
                "[name='lead_name']", "[name='customer_name']",
                "[name='contact_name']"
            ],
            "email": [
                "input[type='email']",
                "input[name*='email' i]",
                "input[id*='email' i]",
                "input[placeholder*='email' i]",
                "input[name='Email']", "input[name='email']",
                "input[data-field*='email' i]",
                "input[class*='email' i]",
                "#email", "#Email",
                "[name='lead_email']", "[name='customer_email']"
            ],
            "phone": [
                "input[type='tel']",
                "input[name*='phone' i]",
                "input[id*='phone' i]",
                "input[placeholder*='phone' i]",
                "input[name*='tel' i]",
                "input[name='Phone']", "input[name='phone']",
                "input[data-field*='phone' i]",
                "input[class*='phone' i]",
                "#phone", "#Phone", "#telephone",
                "[name='lead_phone']", "[name='customer_phone']"
            ],
            "zip": [
                "input[name*='zip' i]",
                "input[id*='zip' i]",
                "input[placeholder*='zip' i]",
                "input[name*='postal' i]",
                "input[name='ZipCode']", "input[name='zip_code']",
                "input[data-field*='zip' i]",
                "#zip", "#zipcode", "#postal",
                "[name='lead_zip']", "[name='customer_zip']"
            ],
            "message": [
                "textarea[name*='message' i]",
                "textarea[name*='comment' i]",
                "textarea[id*='message' i]",
                "textarea[placeholder*='message' i]",
                "textarea[name*='inquiry' i]",
                "textarea[name*='question' i]",
                "textarea[name='Message']", "textarea[name='Comments']",
                "textarea[data-field*='message' i]",
                "textarea", "#message", "#comments",
                "[name='lead_message']", "[name='customer_message']"
            ]
        }

        # Friendly label keywords to help map inputs without descriptive attributes
        self.label_keyword_map = {
            "first_name": ["first name", "given name", "your first name"],
            "last_name": ["last name", "surname", "family name", "your last name"],
            "name": ["full name", "your name"],
            "email": ["email", "e-mail", "mail address"],
            "phone": ["phone", "telephone", "cell", "mobile", "contact number"],
            "zip": ["zip", "postal", "postcode"],
            "message": ["message", "comments", "comment", "question", "questions", "inquiry", "enquiry", "details", "description"],
            "vehicle_interest": ["vehicle", "interest", "model preference"],
            "consent": ["consent", "agree", "authorization", "opt in", "opt-in", "privacy"],
        }
    
    async def detect_contact_form(self, page: Page) -> EnhancedFormResult:
        """Detect contact form with enhanced dynamic content handling"""
        
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
                    "fields_count": len(iframe_result.fields),
                    "iframe_src": iframe_result.iframe_src
                })
                return iframe_result
            
            # Look for forms in main page with multiple strategies
            main_result = await self._detect_forms_in_main_page(page)

            if not main_result.success:
                activated = await self._maybe_trigger_modal_flow(page)
                if activated:
                    self.logger.debug("Modal flow triggered, re-running form detection")
                    await asyncio.sleep(1.0)
                    main_result = await self._detect_forms_in_main_page(page)
            
            self.logger.info("Enhanced form detection completed", {
                "operation": "enhanced_form_detection_complete",
                "success": main_result.success,
                "fields_found": len(main_result.fields),
                "field_types": list(main_result.fields.keys()),
                "confidence": main_result.confidence_score,
                "has_submit": main_result.submit_button is not None
            })
            
            return main_result
            
        except Exception as e:
            self.logger.error("Enhanced form detection failed", {
                "operation": "enhanced_form_detection_error",
                "error": str(e)
            })
            
            return EnhancedFormResult(
                success=False,
                form_element=None,
                fields={},
                submit_button=None,
                confidence_score=0.0
            )
    
    async def _wait_for_dynamic_content(self, page: Page) -> None:
        """Wait for dynamic content to load"""
        
        # Wait for common JavaScript frameworks to load
        await asyncio.sleep(3)  # Increased initial wait
        
        # Wait for common loading indicators to disappear
        loading_selectors = [
            ".loading", ".spinner", ".loader", 
            "[data-loading]", ".sk-loading",
            ".fa-spinner", ".fa-circle-o-notch",
            ".loading-overlay", ".preloader",
            "[aria-label*='loading' i]"
        ]
        
        for selector in loading_selectors:
            try:
                await page.wait_for_selector(selector, state="hidden", timeout=2000)
            except:
                continue
        
        # Wait for forms or inputs to appear with multiple attempts
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                await page.wait_for_selector("form, input, textarea", timeout=3000)
                break
            except:
                attempts += 1
                await asyncio.sleep(1)
        
        # Additional wait for form rendering and JavaScript initialization
        await asyncio.sleep(2)
        
        # Try to trigger any lazy-loaded content by scrolling
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
        except:
            pass
    
    async def _detect_forms_in_main_page(self, page: Page) -> EnhancedFormResult:
        """Detect forms in the main page"""
        
        # Strategy 1: Look for traditional forms
        forms = page.locator("form")
        form_count = await forms.count()
        
        self.logger.debug(f"Found {form_count} forms on main page")
        
        best_form = None
        best_fields = {}
        best_score = 0.0
        
        # Check each form
        for i in range(form_count):
            form = forms.nth(i)
            fields = await self._detect_fields_in_container(form, is_iframe=False)
            score = len(fields) * 0.2
            
            if score > best_score:
                best_score = score
                best_form = form
                best_fields = fields
        
        # Strategy 2: Check whole page if no good forms found
        if form_count == 0 or best_score < 0.4:
            self.logger.debug("No good forms found, checking whole page")
            page_fields = await self._detect_fields_in_container(page, is_iframe=False)
            if len(page_fields) > len(best_fields):
                best_form = None
                best_fields = page_fields
                best_score = len(page_fields) * 0.15
        
        # Find submit button
        submit_button = await self._find_submit_button(best_form or page)
        
        success = len(best_fields) >= 2
        
        return EnhancedFormResult(
            success=success,
            form_element=best_form,
            fields=best_fields,
            submit_button=submit_button,
            confidence_score=best_score
        )
    
    async def _detect_forms_in_iframes(self, page: Page) -> EnhancedFormResult:
        """Detect forms within iframes on the page"""
        
        try:
            # Find all iframes
            iframes = page.locator("iframe")
            iframe_count = await iframes.count()
            
            if iframe_count == 0:
                return EnhancedFormResult(False, None, {}, None, 0.0)
            
            self.logger.debug(f"Found {iframe_count} iframes to check")
            
            for i in range(iframe_count):
                try:
                    iframe = iframes.nth(i)
                    
                    # Get iframe src for logging
                    iframe_src = None
                    try:
                        iframe_src = await iframe.get_attribute("src")
                    except:
                        pass
                    
                    frame = await iframe.content_frame()
                    
                    if frame is None:
                        continue
                    
                    # Wait for iframe content to load
                    await asyncio.sleep(2)
                    
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
                                
                                return EnhancedFormResult(
                                    success=True,
                                    form_element=form,
                                    fields=fields,
                                    submit_button=submit_button,
                                    confidence_score=len(fields) * 0.25,
                                    is_in_iframe=True,
                                    iframe_src=iframe_src
                                )
                
                except Exception as e:
                    self.logger.debug(f"Error checking iframe {i}: {str(e)}")
                    continue
            
            return EnhancedFormResult(False, None, {}, None, 0.0)
            
        except Exception as e:
            self.logger.error(f"Iframe detection failed: {str(e)}")
            return EnhancedFormResult(False, None, {}, None, 0.0)
    
    async def _detect_fields_in_container(self, container: Locator, is_iframe: bool = False) -> Dict[str, EnhancedFormField]:
        """Detect fields in any container"""
        fields = {}
        
        for field_type, selectors in self.field_selectors.items():
            field = await self._find_field_by_selectors(container, selectors, field_type, is_iframe)
            if field:
                fields[field_type] = field

        # Attempt label-based detection for any missing fields
        label_fields = await self._detect_fields_by_labels(container, fields, is_iframe)
        fields.update(label_fields)
        
        return fields
    
    async def _detect_fields_in_iframe_form(self, frame, form: Locator) -> Dict[str, EnhancedFormField]:
        """Detect fields within an iframe form"""
        return await self._detect_fields_in_container(form, is_iframe=True)

    async def _dismiss_cookie_banner(self, page: Page) -> None:
        """Dismiss simple cookie consent banners when present."""

        selectors = [
            "button:has-text('Ok')",
            "button:has-text('OK')",
            "button:has-text('Accept')",
            "button:has-text('Accept All')",
            "button:has-text('I Agree')",
            "button:has-text('Got it')",
            "button:has-text('Allow all')",
        ]

        for selector in selectors:
            try:
                banner = page.locator(selector).first
                if await banner.count() > 0:
                    await banner.click(timeout=2000)
                    await asyncio.sleep(0.5)
                    return
            except Exception:
                continue

        # Some banners use focus traps; remove via JS if button is inaccessible
        try:
            await page.evaluate(
                """
                () => {
                    const banner = document.querySelector('[role="dialog"],[class*="cookie"],[id*="cookie"]');
                    if (banner && banner.parentElement) {
                        banner.parentElement.removeChild(banner);
                    }
                }
                """
            )
        except Exception:
            pass

    async def _dismiss_chat_widgets(self, page: Page) -> None:
        """Attempt to close floating chat widgets that block form controls."""

        # Try common iframe-based chat widgets
        try:
            chat_iframes = page.locator("iframe[src*='livechat'], iframe[src*='webchat'], iframe[src*='salesiq']")
            count = await chat_iframes.count()
            for i in range(count):
                frame = await chat_iframes.nth(i).content_frame()
                if not frame:
                    continue
                try:
                    await frame.locator("button[aria-label*='close'], button:has-text('×')").first.click(timeout=1000)
                except Exception:
                    try:
                        await frame.evaluate("() => document.body.style.display='none'")
                    except Exception:
                        continue
        except Exception:
            pass

        # Non-iframe overlays
        try:
            await page.locator("button[aria-label*='close']:visible").first.click(timeout=1000)
        except Exception:
            pass

        # Hide any sticky chat bubbles by class
        try:
            await page.evaluate(
                """
                () => {
                    const selectors = ['.chat-widget', '.chatbot-launcher', '.zopim', '.intercom-launcher', '.drift-open-chat'];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(node => node.style.display = 'none');
                    });
                }
                """
            )
        except Exception:
            pass

    async def _maybe_trigger_modal_flow(self, page: Page) -> bool:
        """Attempt CTA → department modal → contact form sequence."""

        await self._dismiss_cookie_banner(page)
        await self._dismiss_chat_widgets(page)

        cta_selectors = [
            "a:has-text('Send Us A Message')",
            "button:has-text('Send Us A Message')",
            "a:has-text('Send a message')",
            "button:has-text('Send a message')",
            "a:has-text('Contact Us')",
            "button:has-text('Contact Us')",
        ]

        cta_locator: Optional[Locator] = None
        for selector in cta_selectors:
            try:
                candidate = page.locator(selector)
                if await candidate.count() > 0:
                    cta_locator = candidate.first
                    break
            except Exception:
                continue

        if cta_locator is None:
            return False

        try:
            await cta_locator.scroll_into_view_if_needed()
            await asyncio.sleep(0.6)
            await cta_locator.hover()
            await asyncio.sleep(0.5)
            await cta_locator.click()
        except Exception as exc:
            self.logger.debug(f"CTA click failed: {exc}")
            return False

        await asyncio.sleep(0.8)

        modal = page.locator("[id*='_modal_body_']").first
        try:
            await modal.wait_for(timeout=5000)
        except Exception:
            self.logger.debug("Modal not detected after CTA click")
            return False

        department_selectors = [
            "a:has-text('Sales')",
            "button:has-text('Sales')",
            "a:has-text('New Cars')",
            "button:has-text('New Cars')",
        ]

        department = None
        for selector in department_selectors:
            btn = modal.locator(selector)
            try:
                if await btn.count() > 0:
                    department = btn.first
                    break
            except Exception:
                continue

        if department is None:
            fallback = modal.locator("a, button").first
            if await fallback.count() == 0:
                return False
            department = fallback

        try:
            await department.hover()
            await asyncio.sleep(0.4)
            await department.click()
        except Exception as exc:
            self.logger.debug(f"Department selection failed: {exc}")
            return False

        form_locator = page.locator("form.contactForm, form.lead-form-box")
        try:
            await form_locator.wait_for(timeout=8000)
            await asyncio.sleep(0.8)
        except Exception:
            self.logger.debug("Modal contact form did not appear")
            return False

        self.logger.info("Modal contact flow activated", {"operation": "cta_modal_sales"})
        return True
    
    async def _find_field_by_selectors(self, container: Locator, selectors: List[str], field_type: str, is_iframe: bool = False) -> Optional[EnhancedFormField]:
        """Find field using multiple selectors"""
        
        for selector in selectors:
            try:
                elements = container.locator(selector)
                count = await elements.count()
                
                if count > 0:
                    element = elements.first
                    
                    # Check if it's visible and enabled
                    try:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        
                        if not is_visible or not is_enabled:
                            continue
                    except:
                        pass  # Continue if visibility check fails
                    
                    # Check if it's actually a form field
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea", "select"]:
                        selector_to_use = await self._canonical_selector(element, selector, tag_name)
                        return EnhancedFormField(
                            element=element,
                            field_type=field_type,
                            selector=selector_to_use,
                            confidence=0.8,
                            is_in_iframe=is_iframe
                        )
            except Exception as e:
                prefix = "Iframe" if is_iframe else "Main"
                self.logger.debug(f"{prefix} selector failed: {selector} - {str(e)}")
                continue
        
        return None

    async def _detect_fields_by_labels(self, container: Locator, existing_fields: Dict[str, EnhancedFormField], is_iframe: bool) -> Dict[str, EnhancedFormField]:
        """Infer fields based on associated label text when attributes are generic"""

        try:
            label_data = await container.evaluate(
                """
                (container) => {
                    const escapeSelector = (value) => {
                        if (!value) return null;
                        if (window.CSS && window.CSS.escape) {
                            return CSS.escape(value);
                        }
                        return value.replace(/([ #.;?+*~'":!^$\[\]()=>|\\\/])/g, '\\$1');
                    };

                    const collect = [];
                    const labels = Array.from(container.querySelectorAll('label'));
                    for (const label of labels) {
                        const rawText = label.textContent || '';
                        const text = rawText.trim();
                        if (!text) continue;

                        const forAttr = label.getAttribute('for');
                        let target = null;
                        if (forAttr) {
                            const escaped = escapeSelector(forAttr);
                            if (escaped) {
                                target = container.querySelector(`#${escaped}`);
                            }
                        }
                        if (!target) {
                            const parentGroup = label.closest('.gfield, .field, .form-group, .form-field, li, div');
                            if (parentGroup) {
                                target = parentGroup.querySelector('input, textarea, select');
                            }
                        }
                        if (!target) {
                            const sibling = label.parentElement ? label.parentElement.querySelector('input, textarea, select') : null;
                            if (sibling) target = sibling;
                        }
                        if (!target) continue;

                        const tagName = target.tagName ? target.tagName.toLowerCase() : '';
                        const typeAttr = (target.getAttribute('type') || '').toLowerCase();
                        if (['hidden', 'submit', 'button', 'image'].includes(typeAttr)) continue;

                        const parent = target.closest('li, div, fieldset, section');
                        const classes = parent && parent.classList ? Array.from(parent.classList) : [];
                        const idAttr = target.id || '';
                        const nameAttr = target.getAttribute('name') || '';
                        const placeholder = target.getAttribute('placeholder') || '';
                        const ariaLabel = target.getAttribute('aria-label') || '';

                        collect.push({
                            text,
                            idAttr,
                            nameAttr,
                            tagName,
                            typeAttr,
                            classes,
                            placeholder,
                            ariaLabel,
                        });
                    }
                    return collect;
                }
                """
            )
        except Exception as exc:
            self.logger.debug(f"Label extraction failed: {exc}")
            return {}

        detected: Dict[str, EnhancedFormField] = {}

        for item in label_data:
            field_type = self._infer_field_type_from_label(item.get("text", ""))
            if not field_type:
                continue
            if field_type in existing_fields or field_type in detected:
                continue

            classes = item.get("classes", [])
            # Enhanced honeypot detection with modern patterns
            honeypot_patterns = [
                "gform_validation", "honeypot", "hidden", "invisible", "display-none",
                "visually-hidden", "sr-only", "screen-reader", "bot-trap", "anti-spam",
                "spam-check", "captcha-field", "security-field", "validation-field",
                "form-trap", "robot-check", "bot-field", "fake-field", "decoy-field"
            ]
            if any(pattern in cls.lower() for cls in classes for pattern in honeypot_patterns):
                continue

            # Check field name and ID for honeypot patterns
            field_name = item.get("nameAttr", "").lower()
            field_id = item.get("idAttr", "").lower()
            field_text = item.get("text", "").lower()

            # Common honeypot field names/IDs
            honeypot_names = [
                "url", "website", "homepage", "link", "spam", "bot", "robot",
                "captcha", "security", "validation", "check", "verify", "confirm",
                "test", "fake", "decoy", "trap", "honeypot", "anti-spam"
            ]
            if any(pattern in field_name or pattern in field_id for pattern in honeypot_names):
                continue

            # Skip fields with suspicious text patterns
            suspicious_text = [
                "leave this field blank", "do not fill", "ignore this field",
                "for bots only", "spam protection", "leave empty", "do not enter"
            ]
            if any(pattern in field_text for pattern in suspicious_text):
                continue

            selectors = self._build_candidate_selectors(item)
            for selector in selectors:
                try:
                    locator = container.locator(selector)
                    if await locator.count() == 0:
                        continue
                    element = locator.first
                    try:
                        if not await element.is_enabled():
                            continue
                    except Exception:
                        pass
                    try:
                        await element.is_visible()
                    except Exception:
                        pass

                    canonical_selector = await self._canonical_selector(element, selector, item.get("tagName") or "")

                    detected[field_type] = EnhancedFormField(
                        element=element,
                        field_type=field_type,
                        selector=canonical_selector,
                        confidence=0.9,
                        is_in_iframe=is_iframe
                    )
                    break
                except Exception as exc:
                    self.logger.debug(f"Label selector failed {selector}: {exc}")
                    continue

        return detected

    def _build_candidate_selectors(self, item: Dict[str, str]) -> List[str]:
        selectors: List[str] = []
        tag = item.get("tagName") or "input"
        id_attr = item.get("idAttr") or ""
        name_attr = item.get("nameAttr") or ""
        aria_label = item.get("ariaLabel") or ""
        placeholder = item.get("placeholder") or ""

        if id_attr:
            selectors.append(f"#{id_attr}")
        if name_attr:
            escaped = name_attr.replace('"', '\\"')
            selectors.append(f"{tag}[name=\"{escaped}\"]")
        if aria_label:
            escaped = aria_label.replace('"', '\\"')
            selectors.append(f"{tag}[aria-label=\"{escaped}\"]")
        if placeholder:
            escaped = placeholder.replace('"', '\\"')
            selectors.append(f"{tag}[placeholder=\"{escaped}\"]")

        # Fallback generic type selector
        type_attr = item.get("typeAttr")
        if type_attr and type_attr not in {"text", ""}:
            selectors.append(f"{tag}[type='{type_attr}']")
        if not selectors:
            selectors.append(tag)

        return selectors

    async def _canonical_selector(self, element: Locator, fallback: str, tag_name: str) -> str:
        """Derive a stable selector preference for the detected element."""

        try:
            # Prefer name attribute over ID for reliability with complex IDs
            name_attr = await element.get_attribute("name")
            if name_attr:
                safe = name_attr.replace('"', '\\"')
                # Use attribute selector which is more reliable
                return f"[name=\"{safe}\"]"

            # Fall back to ID only if no name attribute
            element_id = await element.get_attribute("id")
            if element_id:
                # Check if ID needs escaping (starts with digit, has dots, etc)
                needs_escaping = (element_id[0].isdigit() or
                                '.' in element_id or
                                ':' in element_id or
                                ' ' in element_id)

                if needs_escaping:
                    # Use attribute selector for complex IDs
                    safe_id = element_id.replace('"', '\\"')
                    return f"[id=\"{safe_id}\"]"
                else:
                    # Simple ID, use # selector
                    return f"#{element_id}"
        except Exception:
            pass

        return fallback

    def _normalize_label_text(self, text: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
        return normalized

    def _infer_field_type_from_label(self, text: str) -> Optional[str]:
        normalized = self._normalize_label_text(text)
        if not normalized:
            return None

        # Check explicit keyword mappings first
        for field_type, keywords in self.label_keyword_map.items():
            for keyword in keywords:
                if keyword in normalized:
                    if field_type == "vehicle_interest" and "vehicle" not in normalized:
                        continue
                    if field_type == "consent" and "agree" not in normalized and "consent" not in normalized and "opt" not in normalized:
                        continue
                    return field_type

        # Additional basic heuristics
        if "first" in normalized and "name" in normalized:
            return "first_name"
        if "last" in normalized and "name" in normalized:
            return "last_name"
        if "zip" in normalized or "postal" in normalized or "postcode" in normalized:
            return "zip"
        if "phone" in normalized or "telephone" in normalized or "mobile" in normalized:
            return "phone"
        if "email" in normalized:
            return "email"
        if "message" in normalized or "comment" in normalized or "question" in normalized or "inquiry" in normalized or "enquiry" in normalized:
            return "message"
        if "first" in normalized:
            return "first_name"
        if "last" in normalized:
            return "last_name"
        if "name" in normalized:
            return "name"

        return None
    
    async def _find_submit_button(self, container: Locator) -> Optional[Locator]:
        """Find submit button"""
        
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:text('Submit')",
            "button:text('Send')",
            "button:text('Contact')",
            "button:text('Get Quote')",
            "button:text('Request Info')",
            "button:text('Send Message')",
            ".submit-btn", ".btn-submit",
            "#submit", "[data-action='submit']"
        ]
        
        for selector in submit_selectors:
            try:
                buttons = container.locator(selector)
                if await buttons.count() > 0:
                    button = buttons.first
                    # Check if button is visible
                    try:
                        if await button.is_visible():
                            return button
                    except:
                        return button  # Return if visibility check fails
            except Exception:
                continue
        
        return None
    
    async def _find_submit_button_in_frame(self, frame, container: Locator) -> Optional[Locator]:
        """Find submit button within iframe"""
        return await self._find_submit_button(container)
