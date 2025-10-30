"""
Form detection constants - Centralized selectors, patterns, and keywords.

This module contains all the CSS selectors, regex patterns, and keyword mappings
used across the form detection system. Centralizing these makes them easier to:
- Maintain and update
- Test independently
- Share across different detection strategies
- Document and understand

Usage:
    from src.automation.forms.constants import FIELD_SELECTORS, LABEL_KEYWORDS

    email_selectors = FIELD_SELECTORS["email"]
    phone_keywords = LABEL_KEYWORDS["phone"]
"""

from typing import Dict, List

# ==============================================================================
# FIELD SELECTORS
# ==============================================================================

FIELD_SELECTORS: Dict[str, List[str]] = {
    "first_name": [
        # Name-based selectors
        "input[name*='first' i]",
        "input[name*='fname' i]",
        "input[name='FirstName']",
        "input[name='first_name']",
        "[name='lead_first_name']",
        "[name='customer_first_name']",

        # ID-based selectors
        "input[id*='first' i]",
        "input[id*='fname' i]",
        "#firstName",
        "#firstname",
        "#fname",
        "#first_name",

        # Attribute-based selectors
        "input[placeholder*='first' i]",
        "input[data-field*='first' i]",
        "input[class*='first' i]",
    ],

    "last_name": [
        # Name-based selectors
        "input[name*='last' i]",
        "input[name*='lname' i]",
        "input[name='LastName']",
        "input[name='last_name']",
        "[name='lead_last_name']",
        "[name='customer_last_name']",

        # ID-based selectors
        "input[id*='last' i]",
        "input[id*='lname' i]",
        "#lastName",
        "#lastname",
        "#lname",
        "#last_name",

        # Attribute-based selectors
        "input[placeholder*='last' i]",
        "input[data-field*='last' i]",
        "input[class*='last' i]",
    ],

    "name": [
        # Generic name field (when first/last not separated)
        "input[name*='name' i]",
        "input[id*='name' i]",
        "input[placeholder*='name' i]",
        "input[name='Name']",
        "input[name='name']",
        "input[data-field*='name' i]",
        "#name",
        "#fullname",
        "#full_name",
        "[name='lead_name']",
        "[name='customer_name']",
        "[name='contact_name']",
    ],

    "email": [
        # Type-based selector (most reliable)
        "input[type='email']",

        # Name-based selectors
        "input[name*='email' i]",
        "input[name='Email']",
        "input[name='email']",
        "[name='lead_email']",
        "[name='customer_email']",

        # ID-based selectors
        "input[id*='email' i]",
        "#email",
        "#Email",

        # Attribute-based selectors
        "input[placeholder*='email' i]",
        "input[data-field*='email' i]",
        "input[class*='email' i]",
    ],

    "phone": [
        # Type-based selector
        "input[type='tel']",

        # Name-based selectors
        "input[name*='phone' i]",
        "input[name*='tel' i]",
        "input[name='Phone']",
        "input[name='phone']",
        "[name='lead_phone']",
        "[name='customer_phone']",

        # ID-based selectors
        "input[id*='phone' i]",
        "#phone",
        "#Phone",
        "#telephone",

        # Attribute-based selectors
        "input[placeholder*='phone' i]",
        "input[data-field*='phone' i]",
        "input[class*='phone' i]",
    ],

    "zip": [
        # Name-based selectors
        "input[name*='zip' i]",
        "input[name*='postal' i]",
        "input[name='ZipCode']",
        "input[name='zip_code']",
        "[name='lead_zip']",
        "[name='customer_zip']",

        # ID-based selectors
        "input[id*='zip' i]",
        "#zip",
        "#zipcode",
        "#postal",

        # Attribute-based selectors
        "input[placeholder*='zip' i]",
        "input[data-field*='zip' i]",
    ],

    "message": [
        # Textarea selectors (most message fields are textareas)
        "textarea[name*='message' i]",
        "textarea[name*='comment' i]",
        "textarea[name*='inquiry' i]",
        "textarea[name*='question' i]",
        "textarea[id*='message' i]",
        "textarea[placeholder*='message' i]",
        "textarea[name='Message']",
        "textarea[name='Comments']",
        "textarea[data-field*='message' i]",
        "textarea",  # Fallback: any textarea

        # ID-based selectors
        "#message",
        "#comments",

        # Named selectors
        "[name='lead_message']",
        "[name='customer_message']",
    ],

    "vehicle_interest": [
        # Select dropdowns
        "select[name*='vehicle' i]",
        "select[name*='interest' i]",
        "select[name*='model' i]",
        "select[id*='vehicle' i]",
        "select[id*='interest' i]",

        # Text inputs
        "input[name*='vehicle' i]",
        "input[name*='interest' i]",
        "input[placeholder*='vehicle' i]",

        # IDs
        "#vehicle",
        "#vehicleInterest",
        "#modelInterest",
    ],
}

# ==============================================================================
# LABEL KEYWORD MAPPINGS
# ==============================================================================

LABEL_KEYWORDS: Dict[str, List[str]] = {
    "first_name": [
        "first name",
        "given name",
        "your first name",
        "firstname",
    ],

    "last_name": [
        "last name",
        "surname",
        "family name",
        "your last name",
        "lastname",
    ],

    "name": [
        "full name",
        "your name",
        "name",
    ],

    "email": [
        "email",
        "e-mail",
        "mail address",
        "email address",
    ],

    "phone": [
        "phone",
        "telephone",
        "cell",
        "mobile",
        "contact number",
        "phone number",
    ],

    "zip": [
        "zip",
        "postal",
        "postcode",
        "zip code",
        "postal code",
    ],

    "message": [
        "message",
        "comments",
        "comment",
        "question",
        "questions",
        "inquiry",
        "enquiry",
        "details",
        "description",
        "your message",
    ],

    "vehicle_interest": [
        "vehicle",
        "interest",
        "model preference",
        "vehicle of interest",
        "interested in",
    ],

    "consent": [
        "consent",
        "agree",
        "authorization",
        "opt in",
        "opt-in",
        "privacy",
        "terms",
    ],
}

# ==============================================================================
# FORM SELECTORS
# ==============================================================================

FORM_SELECTORS: List[str] = [
    "form[id*='contact' i]",
    "form[class*='contact' i]",
    "form[id*='inquiry' i]",
    "form[class*='inquiry' i]",
    "form[id*='lead' i]",
    "form[class*='lead' i]",
    "form",  # Fallback: any form
]

# ==============================================================================
# SUBMIT BUTTON SELECTORS
# ==============================================================================

SUBMIT_BUTTON_SELECTORS: List[str] = [
    # Type-based (most reliable)
    "button[type='submit']",
    "input[type='submit']",

    # Text-based patterns
    "button:has-text('Submit')",
    "button:has-text('Send')",
    "button:has-text('Contact')",
    "button:has-text('Inquiry')",

    # Class/ID patterns
    "button[class*='submit' i]",
    "button[id*='submit' i]",
    "button[class*='send' i]",
    "button[id*='send' i]",

    # Fallback
    "button",
]

# ==============================================================================
# CONTACT PAGE URL PATTERNS
# ==============================================================================

CONTACT_URL_PATTERNS: List[str] = [
    "/contact",
    "/contact-us",
    "/contactus",
    "/contact_us",
    "/get-in-touch",
    "/inquiry",
    "/enquiry",
    "/reach-us",
]

CONTACT_LINK_TEXT_PATTERNS: List[str] = [
    "contact",
    "contact us",
    "get in touch",
    "reach us",
    "inquiry",
    "enquiry",
]

# ==============================================================================
# IFRAME SELECTORS
# ==============================================================================

IFRAME_SELECTORS: List[str] = [
    "iframe[src*='form']",
    "iframe[src*='contact']",
    "iframe[src*='lead']",
    "iframe[id*='form' i]",
    "iframe[class*='form' i]",
    "iframe",  # Fallback: check all iframes
]

# ==============================================================================
# GRAVITY FORMS PATTERNS (WordPress)
# ==============================================================================

# Gravity Forms uses positional naming (input_1, input_2, etc.)
# Common mappings based on 60% of dealership sites using Gravity Forms
GRAVITY_FORMS_PATTERNS: Dict[str, List[str]] = {
    "first_name": ["input_1", "input_1_3"],  # Often first field
    "last_name": ["input_2", "input_1_6"],   # Often second field
    "email": ["input_3", "input_2"],         # Often third field
    "phone": ["input_4", "input_5"],         # Often fourth/fifth
    "message": ["input_5", "input_6"],       # Usually at end
}

# ==============================================================================
# DEALERSHIP PLATFORM PATTERNS
# ==============================================================================

PLATFORM_PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "stellantis": {
        "first_name": ["#FirstName", "#fname"],
        "last_name": ["#LastName", "#lname"],
        "email": ["#Email", "#email"],
        "phone": ["#Phone", "#phone"],
        "message": ["#Message", "#comments"],
    },

    "cdk_global": {
        "first_name": ["[name='customer_first_name']"],
        "last_name": ["[name='customer_last_name']"],
        "email": ["[name='customer_email']"],
        "phone": ["[name='customer_phone']"],
        "message": ["[name='customer_message']"],
    },

    "dealer_inspire": {
        "first_name": ["[name='lead_first_name']"],
        "last_name": ["[name='lead_last_name']"],
        "email": ["[name='lead_email']"],
        "phone": ["[name='lead_phone']"],
        "message": ["[name='lead_message']"],
    },
}

# ==============================================================================
# TIMEOUTS AND DELAYS
# ==============================================================================

# Wait times for dynamic content loading (milliseconds)
WAIT_FOR_CONTENT_TIMEOUT = 5000  # 5 seconds
WAIT_AFTER_PAGE_LOAD = 2000      # 2 seconds
WAIT_AFTER_CLICK = 1000          # 1 second
WAIT_FOR_FORM_ANIMATION = 500    # 500ms for CSS animations

# ==============================================================================
# CONFIDENCE THRESHOLDS
# ==============================================================================

MIN_CONFIDENCE_SCORE = 0.6      # Minimum confidence to consider detection successful
HIGH_CONFIDENCE_SCORE = 0.8     # High confidence threshold
PERFECT_CONFIDENCE_SCORE = 1.0  # All required fields found

# Required fields for minimum viable contact form
REQUIRED_FIELDS = ["email"]  # At minimum, need email
PREFERRED_FIELDS = ["first_name", "last_name", "email", "phone", "message"]
