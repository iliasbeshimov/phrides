"""
Advanced form detection strategies for dealership websites.
Implements multiple detection approaches with cascading fallbacks.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from playwright.async_api import Page, Locator
from bs4 import BeautifulSoup
import difflib

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FormField:
    """Represents a detected form field"""
    element: Locator
    field_type: str  # first_name, last_name, email, phone, message, vehicle_interest
    confidence: float
    selectors: List[str]
    detection_method: str
    attributes: Dict[str, str]


@dataclass
class FormDetectionResult:
    """Result of form detection process"""
    success: bool
    form_element: Optional[Locator]
    fields: Dict[str, FormField]
    submit_button: Optional[Locator]
    detection_strategy: str
    confidence_score: float
    metadata: Dict


class FormDetectionStrategy:
    """Base class for form detection strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
    
    async def detect_form(self, page: Page) -> FormDetectionResult:
        """Detect contact form on the page"""
        raise NotImplementedError
    
    def _calculate_confidence(self, fields: Dict[str, FormField]) -> float:
        """Calculate overall confidence score for detected form"""
        if not fields:
            return 0.0
        
        # Weight different field types by importance
        field_weights = {
            "first_name": 0.20,
            "last_name": 0.20, 
            "email": 0.25,
            "phone": 0.15,
            "message": 0.10,
            "vehicle_interest": 0.10
        }
        
        total_confidence = 0.0
        total_weight = 0.0
        
        for field_type, field in fields.items():
            if field_type in field_weights:
                weight = field_weights[field_type]
                total_confidence += field.confidence * weight
                total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0


class PreMappedFormStrategy(FormDetectionStrategy):
    """Uses pre-configured mappings for known dealership platforms"""
    
    def __init__(self):
        super().__init__("PreMappedForm")
        self.platform_mappings = self._load_platform_mappings()
    
    def _load_platform_mappings(self) -> Dict:
        """Load pre-configured form mappings for known platforms"""
        return {
            "stellantis_dealer": {
                "domain_patterns": [
                    r".*stellantis.*",
                    r".*chrysler.*",
                    r".*jeep.*",
                    r".*dodge.*",
                    r".*ram.*"
                ],
                "form_selectors": [
                    "#contact-form",
                    ".contact-form", 
                    "form[name='contact']",
                    ".lead-form"
                ],
                "field_mappings": {
                    "first_name": [
                        "input[name='firstName']",
                        "input[name='fname']", 
                        "input[name='first_name']",
                        "#firstName",
                        "#fname"
                    ],
                    "last_name": [
                        "input[name='lastName']",
                        "input[name='lname']",
                        "input[name='last_name']", 
                        "#lastName",
                        "#lname"
                    ],
                    "email": [
                        "input[type='email']",
                        "input[name='email']",
                        "#email",
                        "#emailAddress"
                    ],
                    "phone": [
                        "input[type='tel']",
                        "input[name='phone']",
                        "input[name='telephone']",
                        "#phone",
                        "#phoneNumber"
                    ],
                    "message": [
                        "textarea[name='message']",
                        "textarea[name='comments']",
                        "textarea[name='inquiry']",
                        "#message",
                        "#comments"
                    ],
                    "vehicle_interest": [
                        "select[name='vehicleOfInterest']",
                        "select[name='model']",
                        "select[name='vehicle']",
                        "#vehicleOfInterest"
                    ]
                },
                "submit_selectors": [
                    "button[type='submit']",
                    "input[type='submit']", 
                    ".submit-btn",
                    "#submit",
                    "button.btn-submit"
                ]
            },
            
            "cdk_global": {
                "domain_patterns": [
                    r".*cdk.*",
                    r".*dealeron.*",
                    r".*fortera.*"
                ],
                "form_selectors": [
                    ".lead-form",
                    "#leadForm",
                    ".inquiry-form",
                    ".contact-dealer-form"
                ],
                "field_mappings": {
                    "first_name": [
                        "#lead_customer_first_name",
                        "input[name*='first']",
                        "input[data-name='first_name']"
                    ],
                    "last_name": [
                        "#lead_customer_last_name", 
                        "input[name*='last']",
                        "input[data-name='last_name']"
                    ],
                    "email": [
                        "#lead_customer_email",
                        "input[name*='email']",
                        "input[data-name='email']"
                    ],
                    "phone": [
                        "#lead_customer_primary_phone",
                        "input[name*='phone']",
                        "input[data-name='phone']"
                    ]
                }
            },
            
            "autotrader_cox": {
                "domain_patterns": [
                    r".*autotrader.*",
                    r".*vinsolutions.*",
                    r".*xtime.*"
                ],
                "form_selectors": [
                    ".at-form",
                    "#contact_form", 
                    ".vdp-contact-form"
                ],
                "field_mappings": {
                    "first_name": [
                        "#at_first_name",
                        "input[placeholder*='First']",
                        "input[name='first_name']"
                    ],
                    "last_name": [
                        "#at_last_name",
                        "input[placeholder*='Last']", 
                        "input[name='last_name']"
                    ]
                }
            }
        }
    
    async def detect_form(self, page: Page) -> FormDetectionResult:
        """Detect form using pre-mapped patterns"""
        
        self.logger.debug("Starting pre-mapped form detection", {
            "operation": "premapped_detection_start",
            "url": page.url,
            "platforms_available": len(self.platform_mappings)
        })
        
        # Identify platform based on URL/content
        platform = await self._identify_platform(page)
        
        if not platform:
            self.logger.debug("No matching platform found", {
                "operation": "premapped_no_platform",
                "url": page.url
            })
            return FormDetectionResult(
                success=False,
                form_element=None,
                fields={},
                submit_button=None,
                detection_strategy=self.name,
                confidence_score=0.0,
                metadata={"reason": "no_matching_platform"}
            )
        
        mapping = self.platform_mappings[platform]
        
        # Find form element
        form_element = await self._find_form_element(page, mapping["form_selectors"])
        if not form_element:
            self.logger.debug("No form element found", {
                "operation": "premapped_no_form",
                "platform": platform,
                "selectors_tried": mapping["form_selectors"]
            })
            return FormDetectionResult(
                success=False,
                form_element=None,
                fields={},
                submit_button=None,
                detection_strategy=self.name,
                confidence_score=0.0,
                metadata={"reason": "no_form_element", "platform": platform}
            )
        
        # Map form fields
        fields = await self._map_form_fields(form_element, mapping["field_mappings"])
        
        # Find submit button
        submit_button = await self._find_submit_button(form_element, mapping.get("submit_selectors", []))
        
        confidence = self._calculate_confidence(fields)
        
        self.logger.info("Pre-mapped form detection completed", {
            "operation": "premapped_detection_complete",
            "platform": platform,
            "fields_found": len(fields),
            "field_types": list(fields.keys()),
            "confidence": confidence,
            "has_submit": submit_button is not None
        })
        
        return FormDetectionResult(
            success=len(fields) >= 2,  # Minimum 2 fields required
            form_element=form_element,
            fields=fields,
            submit_button=submit_button,
            detection_strategy=self.name,
            confidence_score=confidence,
            metadata={"platform": platform, "mapping_used": mapping}
        )
    
    async def _identify_platform(self, page: Page) -> Optional[str]:
        """Identify which platform the dealership is using"""
        
        url = page.url.lower()
        page_content = await page.content()
        content_lower = page_content.lower()
        
        for platform, config in self.platform_mappings.items():
            # Check URL patterns
            for pattern in config["domain_patterns"]:
                if re.search(pattern, url):
                    return platform
            
            # Check page content for platform indicators
            platform_indicators = {
                "cdk_global": ["cdk-global", "dealeron", "fortera"],
                "autotrader_cox": ["autotrader", "vinsolutions", "xtime"],
                "stellantis_dealer": ["stellantis", "fca", "mopar"]
            }
            
            if platform in platform_indicators:
                for indicator in platform_indicators[platform]:
                    if indicator in content_lower:
                        return platform
        
        return None
    
    async def _find_form_element(self, page: Page, selectors: List[str]) -> Optional[Locator]:
        """Find the main form element using provided selectors"""
        
        for selector in selectors:
            try:
                forms = page.locator(selector)
                count = await forms.count()
                
                if count > 0:
                    # If multiple forms, pick the most likely contact form
                    if count == 1:
                        return forms.first
                    else:
                        return await self._select_best_form(forms)
                        
            except Exception as e:
                self.logger.debug(f"Selector failed: {selector}", {
                    "operation": "form_selector_failed",
                    "selector": selector,
                    "error": str(e)
                })
                continue
        
        return None
    
    async def _select_best_form(self, forms: Locator) -> Optional[Locator]:
        """Select the best form when multiple are found"""
        
        count = await forms.count()
        best_form = None
        best_score = 0
        
        for i in range(count):
            form = forms.nth(i)
            score = await self._score_form_relevance(form)
            
            if score > best_score:
                best_score = score
                best_form = form
        
        return best_form
    
    async def _score_form_relevance(self, form: Locator) -> int:
        """Score form relevance for contact purposes"""
        
        score = 0
        
        try:
            # Check form attributes
            form_html = await form.inner_html()
            form_text = await form.inner_text()
            
            # Positive indicators
            contact_keywords = [
                "contact", "inquiry", "quote", "information", 
                "interest", "lead", "dealer", "sales"
            ]
            
            for keyword in contact_keywords:
                if keyword in form_html.lower() or keyword in form_text.lower():
                    score += 10
            
            # Check for relevant input types
            if 'type="email"' in form_html:
                score += 15
            if 'type="tel"' in form_html:
                score += 10
            if '<textarea' in form_html:
                score += 10
            
            # Negative indicators
            negative_keywords = [
                "login", "signin", "password", "register", 
                "newsletter", "search", "filter"
            ]
            
            for keyword in negative_keywords:
                if keyword in form_html.lower():
                    score -= 20
                    
        except Exception:
            pass
        
        return score
    
    async def _map_form_fields(self, form: Locator, field_mappings: Dict) -> Dict[str, FormField]:
        """Map form fields using provided mappings"""
        
        fields = {}
        
        for field_type, selectors in field_mappings.items():
            field = await self._find_field_by_selectors(form, selectors, field_type)
            if field:
                fields[field_type] = field
        
        return fields
    
    async def _find_field_by_selectors(self, form: Locator, selectors: List[str], field_type: str) -> Optional[FormField]:
        """Find a field using multiple selector strategies"""
        
        for selector in selectors:
            try:
                elements = form.locator(selector)
                count = await elements.count()
                
                if count > 0:
                    element = elements.first
                    
                    # Verify element is actually a form field
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ["input", "textarea", "select"]:
                        
                        # Get element attributes
                        attributes = await self._get_element_attributes(element)
                        
                        return FormField(
                            element=element,
                            field_type=field_type,
                            confidence=0.9,  # High confidence for pre-mapped
                            selectors=[selector],
                            detection_method="pre_mapped",
                            attributes=attributes
                        )
                        
            except Exception as e:
                self.logger.debug(f"Field selector failed: {selector}", {
                    "operation": "field_selector_failed",
                    "field_type": field_type,
                    "selector": selector,
                    "error": str(e)
                })
                continue
        
        return None
    
    async def _find_submit_button(self, form: Locator, selectors: List[str]) -> Optional[Locator]:
        """Find submit button using provided selectors"""
        
        for selector in selectors:
            try:
                buttons = form.locator(selector)
                count = await buttons.count()
                
                if count > 0:
                    return buttons.first
                    
            except Exception:
                continue
        
        # Fallback: look for any submit button
        try:
            submit_buttons = form.locator("button[type='submit'], input[type='submit']")
            if await submit_buttons.count() > 0:
                return submit_buttons.first
        except Exception:
            pass
        
        return None
    
    async def _get_element_attributes(self, element: Locator) -> Dict[str, str]:
        """Get all relevant attributes from an element"""
        
        attributes = {}
        
        try:
            # Standard attributes to collect
            attr_names = ["name", "id", "class", "type", "placeholder", "required", "value"]
            
            for attr in attr_names:
                value = await element.get_attribute(attr)
                if value:
                    attributes[attr] = value
                    
        except Exception:
            pass
        
        return attributes


class SemanticFormStrategy(FormDetectionStrategy):
    """Intelligent form field detection using semantic analysis"""
    
    def __init__(self):
        super().__init__("SemanticForm")
        self.field_patterns = self._load_semantic_patterns()
    
    def _load_semantic_patterns(self) -> Dict:
        """Load semantic patterns for field detection"""
        return {
            "first_name": {
                "name_patterns": [
                    r"first.*name", r"fname", r"given.*name", 
                    r"contact.*first", r"customer.*first"
                ],
                "placeholder_patterns": [
                    r"first.*name", r"your.*first.*name", 
                    r"enter.*first", r"given.*name"
                ],
                "label_patterns": [
                    "first name", "first", "given name", "fname"
                ],
                "id_class_patterns": [
                    r"first", r"fname", r"given"
                ]
            },
            
            "last_name": {
                "name_patterns": [
                    r"last.*name", r"lname", r"surname", 
                    r"family.*name", r"contact.*last"
                ],
                "placeholder_patterns": [
                    r"last.*name", r"your.*last.*name", 
                    r"enter.*last", r"surname"
                ],
                "label_patterns": [
                    "last name", "last", "surname", "family name", "lname"
                ],
                "id_class_patterns": [
                    r"last", r"lname", r"surname"
                ]
            },
            
            "email": {
                "name_patterns": [
                    r"email", r"e-mail", r"mail", r"email.*address"
                ],
                "placeholder_patterns": [
                    r"email", r"e-mail", r"your.*email", 
                    r"enter.*email", r"email.*address"
                ],
                "label_patterns": [
                    "email", "e-mail", "email address", "mail"
                ],
                "id_class_patterns": [
                    r"email", r"mail"
                ],
                "type_indicators": ["email"]
            },
            
            "phone": {
                "name_patterns": [
                    r"phone", r"tel", r"mobile", r"cell", 
                    r"telephone", r"contact.*number"
                ],
                "placeholder_patterns": [
                    r"phone", r"telephone", r"mobile", r"cell",
                    r"your.*phone", r"phone.*number"
                ],
                "label_patterns": [
                    "phone", "telephone", "mobile", "cell", 
                    "phone number", "contact number"
                ],
                "id_class_patterns": [
                    r"phone", r"tel", r"mobile", r"cell"
                ],
                "type_indicators": ["tel"]
            },
            
            "message": {
                "name_patterns": [
                    r"message", r"comment", r"inquiry", r"details", 
                    r"notes", r"question", r"body"
                ],
                "placeholder_patterns": [
                    r"message", r"comment", r"inquiry", r"details",
                    r"your.*message", r"enter.*message"
                ],
                "label_patterns": [
                    "message", "comments", "inquiry", "details", 
                    "notes", "questions", "additional information"
                ],
                "id_class_patterns": [
                    r"message", r"comment", r"inquiry", r"details"
                ],
                "tag_indicators": ["textarea"]
            },
            
            "vehicle_interest": {
                "name_patterns": [
                    r"vehicle", r"model", r"interest", r"looking.*for",
                    r"vehicle.*interest", r"model.*interest"
                ],
                "label_patterns": [
                    "vehicle of interest", "model", "vehicle", 
                    "what are you looking for", "interested in"
                ],
                "id_class_patterns": [
                    r"vehicle", r"model", r"interest"
                ],
                "tag_indicators": ["select"],
                "option_indicators": ["jeep", "ram", "chrysler", "dodge"]
            }
        }
    
    async def detect_form(self, page: Page) -> FormDetectionResult:
        """Detect form using semantic analysis"""
        
        self.logger.debug("Starting semantic form detection", {
            "operation": "semantic_detection_start",
            "url": page.url
        })
        
        # Find all potential forms on the page
        forms = await self._find_all_forms(page)
        
        if not forms:
            return FormDetectionResult(
                success=False,
                form_element=None,
                fields={},
                submit_button=None,
                detection_strategy=self.name,
                confidence_score=0.0,
                metadata={"reason": "no_forms_found"}
            )
        
        # Analyze each form and pick the best one
        best_form_result = None
        best_confidence = 0.0
        
        for form in forms:
            form_result = await self._analyze_form_semantically(form)
            
            if form_result.confidence_score > best_confidence:
                best_confidence = form_result.confidence_score
                best_form_result = form_result
        
        if best_form_result and best_confidence > 0.3:  # Minimum confidence threshold
            self.logger.info("Semantic form detection completed", {
                "operation": "semantic_detection_complete",
                "fields_found": len(best_form_result.fields),
                "field_types": list(best_form_result.fields.keys()),
                "confidence": best_confidence
            })
            return best_form_result
        
        return FormDetectionResult(
            success=False,
            form_element=None,
            fields={},
            submit_button=None,
            detection_strategy=self.name,
            confidence_score=0.0,
            metadata={"reason": "low_confidence", "best_confidence": best_confidence}
        )
    
    async def _find_all_forms(self, page: Page) -> List[Locator]:
        """Find all forms on the page"""
        
        forms = []
        
        # Look for actual form elements
        form_elements = page.locator("form")
        form_count = await form_elements.count()
        
        for i in range(form_count):
            forms.append(form_elements.nth(i))
        
        # Also look for div-based forms (common in modern web apps)
        potential_forms = page.locator("div[class*='form'], div[id*='form'], div[class*='contact'], div[id*='contact']")
        potential_count = await potential_forms.count()
        
        for i in range(potential_count):
            form_div = potential_forms.nth(i)
            
            # Check if it contains form fields
            inputs = form_div.locator("input, textarea, select")
            input_count = await inputs.count()
            
            if input_count >= 2:  # Minimum fields for a form
                forms.append(form_div)
        
        return forms
    
    async def _analyze_form_semantically(self, form: Locator) -> FormDetectionResult:
        """Analyze a form using semantic patterns"""
        
        fields = {}
        
        # Get all form fields
        form_fields = form.locator("input, textarea, select")
        field_count = await form_fields.count()
        
        for i in range(field_count):
            field_element = form_fields.nth(i)
            
            # Analyze this field
            field_analysis = await self._analyze_field_semantically(field_element)
            
            if field_analysis:
                field_type = field_analysis["field_type"]
                confidence = field_analysis["confidence"]
                
                # Only keep if confidence is reasonable or if we don't have this field type yet
                if confidence > 0.4 or field_type not in fields:
                    if field_type not in fields or confidence > fields[field_type].confidence:
                        fields[field_type] = FormField(
                            element=field_element,
                            field_type=field_type,
                            confidence=confidence,
                            selectors=field_analysis["selectors"],
                            detection_method="semantic",
                            attributes=field_analysis["attributes"]
                        )
        
        # Find submit button
        submit_button = await self._find_submit_button_semantic(form)
        
        confidence = self._calculate_confidence(fields)
        
        return FormDetectionResult(
            success=len(fields) >= 2,
            form_element=form,
            fields=fields,
            submit_button=submit_button,
            detection_strategy=self.name,
            confidence_score=confidence,
            metadata={"semantic_analysis": True}
        )
    
    async def _analyze_field_semantically(self, field: Locator) -> Optional[Dict]:
        """Analyze a single field using semantic patterns"""
        
        try:
            # Get field attributes and context
            tag_name = await field.evaluate("el => el.tagName.toLowerCase()")
            field_type = await field.get_attribute("type") or ""
            name_attr = await field.get_attribute("name") or ""
            id_attr = await field.get_attribute("id") or ""
            class_attr = await field.get_attribute("class") or ""
            placeholder = await field.get_attribute("placeholder") or ""
            
            # Get associated label text
            label_text = await self._get_associated_label_text(field)
            
            # Get surrounding text context
            surrounding_text = await self._get_surrounding_text(field)
            
            # Combine all text for analysis
            all_text = f"{name_attr} {id_attr} {class_attr} {placeholder} {label_text} {surrounding_text}".lower()
            
            # Score against each field type pattern
            best_match = None
            best_score = 0.0
            
            for field_name, patterns in self.field_patterns.items():
                score = self._calculate_semantic_score(
                    all_text, tag_name, field_type, patterns
                )
                
                if score > best_score:
                    best_score = score
                    best_match = field_name
            
            if best_match and best_score > 0.3:
                return {
                    "field_type": best_match,
                    "confidence": best_score,
                    "selectors": [self._generate_selector(name_attr, id_attr, class_attr)],
                    "attributes": {
                        "name": name_attr,
                        "id": id_attr,
                        "class": class_attr,
                        "type": field_type,
                        "placeholder": placeholder,
                        "tag": tag_name
                    }
                }
            
        except Exception as e:
            self.logger.debug("Field analysis failed", {
                "operation": "semantic_field_analysis_failed",
                "error": str(e)
            })
        
        return None
    
    def _calculate_semantic_score(self, text: str, tag_name: str, field_type: str, patterns: Dict) -> float:
        """Calculate semantic match score for a field"""
        
        score = 0.0
        
        # Check type indicators
        if "type_indicators" in patterns:
            if field_type in patterns["type_indicators"]:
                score += 0.4
        
        # Check tag indicators
        if "tag_indicators" in patterns:
            if tag_name in patterns["tag_indicators"]:
                score += 0.3
        
        # Check name patterns
        if "name_patterns" in patterns:
            for pattern in patterns["name_patterns"]:
                if re.search(pattern, text):
                    score += 0.2
                    break
        
        # Check placeholder patterns
        if "placeholder_patterns" in patterns:
            for pattern in patterns["placeholder_patterns"]:
                if re.search(pattern, text):
                    score += 0.15
                    break
        
        # Check label patterns
        if "label_patterns" in patterns:
            for pattern in patterns["label_patterns"]:
                if pattern in text:
                    score += 0.15
                    break
        
        # Check ID/class patterns
        if "id_class_patterns" in patterns:
            for pattern in patterns["id_class_patterns"]:
                if re.search(pattern, text):
                    score += 0.1
                    break
        
        # Special case for vehicle interest - check for option indicators
        if "option_indicators" in patterns:
            # This would require checking select options, implement if needed
            pass
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _get_associated_label_text(self, field: Locator) -> str:
        """Get label text associated with the field"""
        
        try:
            # Try to find label by 'for' attribute
            field_id = await field.get_attribute("id")
            if field_id:
                label = field.page.locator(f"label[for='{field_id}']")
                if await label.count() > 0:
                    return await label.inner_text()
            
            # Try to find parent label
            parent_label = field.locator("xpath=ancestor::label[1]")
            if await parent_label.count() > 0:
                return await parent_label.inner_text()
            
            # Try to find preceding label
            preceding_label = field.locator("xpath=preceding-sibling::label[1]")
            if await preceding_label.count() > 0:
                return await preceding_label.inner_text()
                
        except Exception:
            pass
        
        return ""
    
    async def _get_surrounding_text(self, field: Locator) -> str:
        """Get surrounding text context for the field"""
        
        try:
            # Get parent element text
            parent = field.locator("xpath=..")
            parent_text = await parent.inner_text()
            
            # Clean up and limit text
            words = parent_text.split()
            if len(words) > 20:
                words = words[:20]
            
            return " ".join(words)
            
        except Exception:
            return ""
    
    def _generate_selector(self, name: str, id_attr: str, class_attr: str) -> str:
        """Generate CSS selector for the field"""
        
        if id_attr:
            return f"#{id_attr}"
        elif name:
            return f"[name='{name}']"
        elif class_attr:
            # Use first class
            first_class = class_attr.split()[0] if class_attr.split() else class_attr
            return f".{first_class}"
        else:
            return "input"  # Generic fallback
    
    async def _find_submit_button_semantic(self, form: Locator) -> Optional[Locator]:
        """Find submit button using semantic analysis"""
        
        # Look for explicit submit buttons
        submit_buttons = form.locator("button[type='submit'], input[type='submit']")
        if await submit_buttons.count() > 0:
            return submit_buttons.first
        
        # Look for buttons with submit-like text
        buttons = form.locator("button, input[type='button']")
        button_count = await buttons.count()
        
        submit_keywords = [
            "submit", "send", "contact", "inquire", "get quote", 
            "request", "continue", "next", "go"
        ]
        
        for i in range(button_count):
            button = buttons.nth(i)
            try:
                button_text = await button.inner_text()
                button_value = await button.get_attribute("value") or ""
                
                combined_text = f"{button_text} {button_value}".lower()
                
                for keyword in submit_keywords:
                    if keyword in combined_text:
                        return button
                        
            except Exception:
                continue
        
        return None