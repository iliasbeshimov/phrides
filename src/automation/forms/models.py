"""
Unified data models for form detection.

This module provides standardized dataclasses for representing form detection
results across all detection strategies. Previously, different detectors used
slightly different data models (FormField vs EnhancedFormField), causing
inconsistencies. These unified models work with all detection approaches.

Usage:
    from src.automation.forms.models import FormField, FormDetectionResult

    field = FormField(
        element=locator,
        field_type="email",
        confidence=0.95,
        selector="input[type='email']"
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from playwright.async_api import Locator


@dataclass
class FormField:
    """
    Unified form field representation.

    Combines the best features from FormField and EnhancedFormField:
    - Basic field information (element, type, confidence)
    - Multiple selector tracking (for debugging and logging)
    - Detection metadata (method, attributes)
    - iframe support (for embedded forms)

    Attributes:
        element: Playwright Locator for the form field
        field_type: Type of field (first_name, last_name, email, phone, message, etc.)
        confidence: Confidence score (0.0-1.0) for detection accuracy
        selector: Primary CSS selector that located this field
        selectors: All selectors that were attempted (for debugging)
        detection_method: Strategy that found this field (semantic, visual, pre-mapped, etc.)
        attributes: HTML attributes of the element (name, id, class, placeholder, etc.)
        is_in_iframe: Whether this field is inside an iframe
        label_text: Associated label text, if found
    """
    element: Locator
    field_type: str
    confidence: float
    selector: str
    selectors: List[str] = field(default_factory=list)
    detection_method: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
    is_in_iframe: bool = False
    label_text: Optional[str] = None


@dataclass
class FormDetectionResult:
    """
    Result of form detection process.

    Unified result format that works with all detection strategies.
    Provides comprehensive information about:
    - Whether detection succeeded
    - What form and fields were found
    - Confidence scores
    - Metadata for debugging and logging

    Attributes:
        success: Whether a valid form was detected
        form_element: The <form> element (or container if no explicit form tag)
        fields: Dictionary mapping field_type to FormField objects
        submit_button: Submit button locator
        detection_strategy: Which strategy found this form (semantic, visual, etc.)
        confidence_score: Overall confidence (0.0-1.0)
        metadata: Additional information (platform detected, iframe info, etc.)
        is_in_iframe: Whether the form is inside an iframe
        iframe_src: Source URL of the iframe (if applicable)
    """
    success: bool
    form_element: Optional[Locator]
    fields: Dict[str, FormField]
    submit_button: Optional[Locator]
    detection_strategy: str
    confidence_score: float
    metadata: Dict = field(default_factory=dict)
    is_in_iframe: bool = False
    iframe_src: Optional[str] = None

    def has_field(self, field_type: str) -> bool:
        """Check if a specific field type was found."""
        return field_type in self.fields

    def get_required_fields(self, required: List[str]) -> Dict[str, FormField]:
        """Get only the required fields (returns empty dict if any missing)."""
        if all(self.has_field(ft) for ft in required):
            return {ft: self.fields[ft] for ft in required}
        return {}

    def missing_fields(self, required: List[str]) -> List[str]:
        """Return list of required fields that are missing."""
        return [ft for ft in required if not self.has_field(ft)]

    def field_count(self) -> int:
        """Return total number of fields detected."""
        return len(self.fields)


@dataclass
class ContactPageResult:
    """
    Result of contact page discovery.

    Used by contact page finders to report discovered URLs.

    Attributes:
        found: Whether a contact page was found
        url: URL of the contact page
        confidence: Confidence score (0.0-1.0)
        discovery_method: How the page was found (direct URL, link text, etc.)
        metadata: Additional info (link text, parent page, etc.)
    """
    found: bool
    url: Optional[str]
    confidence: float
    discovery_method: str
    metadata: Dict = field(default_factory=dict)


# Backward compatibility aliases
# These allow existing code to keep working while migrating to unified models
EnhancedFormField = FormField  # Old name from enhanced_form_detector.py
EnhancedFormResult = FormDetectionResult  # Old name from enhanced_form_detector.py


# Constants for field types (for type checking and validation)
FIELD_TYPES = {
    "first_name",
    "last_name",
    "name",           # Full name (when first/last not separate)
    "email",
    "phone",
    "zip",
    "message",
    "vehicle_interest",
    "consent",
}
