# Comprehensive Tracking States Specification

## Overview

This document defines **all possible states** for each step of the automated contact form submission process, with clear, self-explanatory terminology.

---

## State Hierarchy

```
DEALERSHIP PROCESSING
├── CONTACT_PAGE_DISCOVERY
├── FORM_DETECTION
├── FIELD_IDENTIFICATION
├── FORM_FILLING
├── FORM_SUBMISSION
└── OVERALL_STATUS
```

---

## 1. CONTACT_PAGE_DISCOVERY States

### Primary States
| State | Meaning | Next Step |
|-------|---------|-----------|
| `CONTACT_PAGE_FOUND` | Successfully found contact page URL | Proceed to form detection |
| `CONTACT_PAGE_NOT_FOUND` | No contact page URL discovered after all attempts | TERMINAL - Manual intervention |
| `CONTACT_PAGE_CACHED` | Contact page URL retrieved from cache | Proceed to form detection |
| `HOMEPAGE_LOAD_FAILED` | Could not load dealership homepage | TERMINAL - Network/site issue |
| `CONTACT_PAGE_LOAD_FAILED` | Found URL but page won't load | Try alternative URL or TERMINAL |

### Discovery Method (when found)
| Method | Meaning |
|--------|---------|
| `CACHE_HIT` | Retrieved from previous successful discovery |
| `HOMEPAGE_LINK_ANALYSIS` | Found by analyzing links on homepage |
| `COMMON_PATTERN_MATCH` | Found by testing common URL patterns (/contact.htm, /contactus.aspx) |
| `SITEMAP_DISCOVERY` | Found in sitemap.xml |
| `GOOGLE_SEARCH` | Found via Google Custom Search API |

### Metadata
```json
{
  "discovery_state": "CONTACT_PAGE_FOUND",
  "discovery_method": "COMMON_PATTERN_MATCH",
  "contact_url": "https://dealer.com/contactus.aspx",
  "urls_attempted": 3,
  "discovery_time_ms": 2500,
  "cached": false
}
```

---

## 2. FORM_DETECTION States

### Primary States
| State | Meaning | Next Step |
|-------|---------|-----------|
| `FORM_DETECTED_VALID` | Form found with ≥4 required fields | Proceed to field identification |
| `FORM_DETECTED_WEAK` | Form found but <4 fields (insufficient) | Try next contact URL or TERMINAL |
| `FORM_NOT_DETECTED` | No form elements found on page | Try next contact URL or TERMINAL |
| `MULTIPLE_FORMS_FOUND` | Multiple forms detected, selected best one | Proceed to field identification |
| `FORM_IN_IFRAME` | Form embedded in iframe (switched context) | Proceed to field identification |
| `FORM_REQUIRES_JAVASCRIPT` | Form loads dynamically (waited for render) | Proceed to field identification |

### Form Quality
| Quality | Criteria |
|---------|----------|
| `HIGH_QUALITY` | ≥6 fields, has email + submit button, confidence ≥1.5 |
| `MEDIUM_QUALITY` | 4-5 fields, has email + submit button, confidence 0.8-1.5 |
| `LOW_QUALITY` | <4 fields or missing critical elements |

### Metadata
```json
{
  "detection_state": "FORM_DETECTED_VALID",
  "form_quality": "HIGH_QUALITY",
  "form_field_count": 8,
  "confidence_score": 1.6,
  "has_submit_button": true,
  "is_iframe": false,
  "platform_detected": "dealer.com",
  "detection_time_ms": 2100
}
```

---

## 3. FIELD_IDENTIFICATION States

### Per-Field States
| State | Meaning |
|-------|---------|
| `FIELD_IDENTIFIED_STANDARD` | Standard field identified (name, email, phone, etc.) |
| `FIELD_IDENTIFIED_COMPLEX` | Complex field identified (split phone, gravity forms, etc.) |
| `FIELD_IDENTIFIED_HONEYPOT` | Honeypot trap field detected |
| `FIELD_IDENTIFIED_UNKNOWN` | Field detected but type unknown |
| `FIELD_IDENTIFIED_CAPTCHA` | CAPTCHA field detected |

### Field Categories
| Category | Fields Included |
|----------|----------------|
| `REQUIRED_FIELDS` | first_name, last_name, email, phone, message |
| `OPTIONAL_FIELDS` | zip_code, vehicle_interest, preferred_contact, company |
| `CONSENT_FIELDS` | privacy_policy, terms_and_conditions, marketing_consent |
| `HONEYPOT_FIELDS` | Hidden trap fields to detect bots |
| `CAPTCHA_FIELDS` | reCAPTCHA, hCaptcha, etc. |

### Complex Field Types
| Type | Pattern |
|------|---------|
| `SPLIT_PHONE` | Phone number split into 3 inputs (area code, prefix, suffix) |
| `GRAVITY_FORMS_NAME` | First/Last name in sub-labeled fields |
| `GRAVITY_FORMS_ZIP` | Gravity Forms specific zip code field |
| `CUSTOM_DROPDOWN` | React/Vue custom select component |
| `DATE_PICKER` | Calendar widget for date selection |
| `FILE_UPLOAD` | File attachment field |

### Metadata
```json
{
  "identification_state": "FIELDS_IDENTIFIED",
  "total_fields": 8,
  "fields_by_category": {
    "required": ["first_name", "last_name", "email", "phone", "message"],
    "optional": ["zip_code"],
    "consent": ["privacy_consent"],
    "honeypot": ["website_url"]
  },
  "complex_fields": [
    {"type": "SPLIT_PHONE", "detected": true}
  ],
  "identification_time_ms": 500
}
```

---

## 4. FORM_FILLING States

### Overall Filling States
| State | Meaning | Next Step |
|-------|---------|-----------|
| `FORM_FILLED_COMPLETE` | All required fields filled successfully | Proceed to submission |
| `FORM_FILLED_PARTIAL` | Some fields filled, some failed/skipped | Proceed to submission (may fail) |
| `FORM_FILLING_FAILED` | Could not fill any fields | TERMINAL - Technical issue |

### Per-Field Filling States
| State | Meaning |
|-------|---------|
| `FIELD_FILLED_SUCCESS` | Field filled with test data successfully |
| `FIELD_SKIPPED_HONEYPOT` | Intentionally skipped (honeypot detected) |
| `FIELD_SKIPPED_COMPLEX_HANDLED` | Skipped because handled by complex field handler |
| `FIELD_SKIPPED_NO_DATA` | No test data available for this field type |
| `FIELD_FILLED_FAILED` | Attempted to fill but error occurred |
| `FIELD_SKIPPED_READONLY` | Field is read-only or disabled |
| `FIELD_SKIPPED_HIDDEN` | Field is hidden (likely honeypot) |

### Filling Quality Metrics
| Metric | Meaning |
|--------|---------|
| `fill_rate` | Percentage of fields successfully filled |
| `required_fill_rate` | Percentage of required fields filled (most critical) |
| `honeypot_detection_rate` | Percentage of honeypots correctly identified |

### Metadata
```json
{
  "filling_state": "FORM_FILLED_COMPLETE",
  "total_fields": 8,
  "fields_filled": 6,
  "fields_skipped": 2,
  "fill_rate": 0.75,
  "required_fill_rate": 1.0,
  "filling_details": [
    {"field": "first_name", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "last_name", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "email", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "phone", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "zip_code", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "message", "state": "FIELD_FILLED_SUCCESS"},
    {"field": "website_url", "state": "FIELD_SKIPPED_HONEYPOT"},
    {"field": "consent", "state": "FIELD_FILLED_SUCCESS"}
  ],
  "honeypots_detected": 1,
  "complex_fields_filled": [
    {"type": "SPLIT_PHONE", "state": "FIELD_FILLED_SUCCESS"}
  ],
  "filling_time_ms": 4200
}
```

---

## 5. FORM_SUBMISSION States

### Primary States
| State | Meaning | Manual Action |
|-------|---------|---------------|
| `SUBMISSION_VERIFIED_SUCCESS` | Form submitted AND verified successful | ✅ None - Complete |
| `SUBMISSION_UNVERIFIED` | Form submitted but verification uncertain | ⚠️ Manual verification recommended |
| `SUBMISSION_FAILED_BLOCKER` | Submission blocked (CAPTCHA, validation, etc.) | 🔴 Manual submission required |
| `SUBMISSION_FAILED_TECHNICAL` | Technical error during submission | 🔴 Retry or manual submission |
| `SUBMISSION_NOT_ATTEMPTED` | Did not attempt (prior step failed) | 🔴 Fix prior step |

### Submission Methods Used
| Method | When Used |
|--------|-----------|
| `STANDARD_CLICK` | Normal button click (first attempt) |
| `FORCE_CLICK` | Force click to bypass overlays |
| `JAVASCRIPT_CLICK` | JavaScript-triggered click |
| `DISPATCH_EVENT_CLICK` | Manually dispatched click event |
| `ENTER_KEY` | Pressed Enter key to submit |

### Verification Methods
| Method | Reliability | Meaning |
|--------|-------------|---------|
| `URL_CHANGE_VERIFICATION` | 95% | URL changed to thank-you/confirmation page |
| `SUCCESS_MESSAGE_VERIFICATION` | 90% | Success message appeared on page |
| `FORM_HIDDEN_VERIFICATION` | 85% | Form disappeared after submission |
| `THANK_YOU_TEXT_VERIFICATION` | 80% | "Thank you" text found in page content |
| `NETWORK_REQUEST_VERIFICATION` | 98% | POST request returned 200/201/302 |
| `NO_VERIFICATION` | 0% | Could not verify submission |

### Blocker Types
| Blocker | Meaning | Manual Action |
|---------|---------|---------------|
| `CAPTCHA_DETECTED` | reCAPTCHA or hCaptcha present | Manual CAPTCHA solving |
| `VALIDATION_ERROR` | Required field validation failed | Review field mapping |
| `BUTTON_NOT_CLICKABLE` | Submit button obscured/disabled | Manual inspection |
| `FORM_TIMEOUT` | Submission timed out | Retry or manual |
| `NETWORK_ERROR` | Network request failed | Check site status |
| `JAVASCRIPT_ERROR` | JavaScript error prevented submission | Manual submission |

### Metadata
```json
{
  "submission_state": "SUBMISSION_VERIFIED_SUCCESS",
  "submission_method": "STANDARD_CLICK",
  "verification_method": "URL_CHANGE_VERIFICATION",
  "verification_confidence": 0.95,
  "blocker": null,
  "pre_submission_url": "https://dealer.com/contactus.aspx",
  "post_submission_url": "https://dealer.com/thank-you/",
  "success_indicators": [
    "URL changed to /thank-you/",
    "Page contains 'Thank you for contacting us'"
  ],
  "submission_time_ms": 1800,
  "screenshot_before": "tests/.../dealer_filled.png",
  "screenshot_after": "tests/.../dealer_success.png"
}
```

---

## 6. OVERALL_STATUS States

### Terminal States
| State | Success? | Meaning | Manual Action |
|-------|----------|---------|---------------|
| `SUCCESS_COMPLETE` | ✅ Yes | Full automation success - verified submission | None |
| `SUCCESS_UNVERIFIED` | ⚠️ Partial | Submitted but verification uncertain | Verify manually |
| `PARTIAL_FORM_FILLED` | ⚠️ Partial | Form filled but submission failed | Manual submission |
| `BLOCKED_CAPTCHA` | 🔴 No | Blocked by CAPTCHA | Manual CAPTCHA solve + submit |
| `BLOCKED_TECHNICAL` | 🔴 No | Technical blocker (validation, error, etc.) | Manual review + submit |
| `FAILED_NO_FORM` | 🔴 No | No contact form found | Use phone/email/chat |
| `FAILED_NO_CONTACT_PAGE` | 🔴 No | No contact page found | Use phone/email |
| `FAILED_SITE_ERROR` | 🔴 No | Site unreachable or broken | Retry later or phone |
| `FAILED_NETWORK` | 🔴 No | Network/connectivity error | Retry |

### Status Category Grouping
```python
SUCCESS_STATES = ["SUCCESS_COMPLETE", "SUCCESS_UNVERIFIED"]
PARTIAL_STATES = ["PARTIAL_FORM_FILLED"]
BLOCKED_STATES = ["BLOCKED_CAPTCHA", "BLOCKED_TECHNICAL"]
FAILED_STATES = ["FAILED_NO_FORM", "FAILED_NO_CONTACT_PAGE",
                 "FAILED_SITE_ERROR", "FAILED_NETWORK"]

MANUAL_REVIEW_REQUIRED = PARTIAL_STATES + BLOCKED_STATES + FAILED_STATES
```

### Metadata
```json
{
  "overall_status": "SUCCESS_COMPLETE",
  "status_category": "SUCCESS",
  "requires_manual_action": false,
  "manual_action_type": null,
  "total_time_ms": 11600,
  "steps_completed": [
    "CONTACT_PAGE_DISCOVERY",
    "FORM_DETECTION",
    "FIELD_IDENTIFICATION",
    "FORM_FILLING",
    "FORM_SUBMISSION"
  ],
  "failure_point": null,
  "retry_recommended": false,
  "alternative_contact_methods": null
}
```

---

## Complete Tracking Record Example

### Successful Submission
```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-03T18:45:30.123Z",

  "dealership": {
    "name": "Floyd Chrysler Dodge Jeep Ram",
    "website": "https://www.floydcdjr.com",
    "city": "Dunn",
    "state": "NC"
  },

  "contact_page_discovery": {
    "state": "CONTACT_PAGE_FOUND",
    "method": "COMMON_PATTERN_MATCH",
    "contact_url": "https://www.floydcdjr.com/contactus.aspx",
    "urls_attempted": 1,
    "cached": false,
    "time_ms": 3500
  },

  "form_detection": {
    "state": "FORM_DETECTED_VALID",
    "quality": "HIGH_QUALITY",
    "field_count": 8,
    "confidence_score": 1.6,
    "has_submit_button": true,
    "is_iframe": false,
    "platform": "asp.net",
    "time_ms": 2100
  },

  "field_identification": {
    "state": "FIELDS_IDENTIFIED",
    "total_fields": 8,
    "required_fields": ["first_name", "last_name", "email", "phone", "message"],
    "optional_fields": ["zip_code"],
    "consent_fields": ["privacy_consent"],
    "honeypot_fields": [],
    "complex_fields": [
      {"type": "GRAVITY_FORMS_ZIP", "detected": true}
    ],
    "time_ms": 500
  },

  "form_filling": {
    "state": "FORM_FILLED_COMPLETE",
    "fields_filled": 7,
    "fields_skipped": 1,
    "fill_rate": 0.875,
    "required_fill_rate": 1.0,
    "filling_details": [
      {"field": "first_name", "state": "FIELD_FILLED_SUCCESS", "value_type": "text"},
      {"field": "last_name", "state": "FIELD_FILLED_SUCCESS", "value_type": "text"},
      {"field": "email", "state": "FIELD_FILLED_SUCCESS", "value_type": "email"},
      {"field": "phone", "state": "FIELD_FILLED_SUCCESS", "value_type": "phone"},
      {"field": "zip_code", "state": "FIELD_FILLED_SUCCESS", "value_type": "zip", "handler": "GRAVITY_FORMS"},
      {"field": "message", "state": "FIELD_FILLED_SUCCESS", "value_type": "textarea"},
      {"field": "privacy_consent", "state": "FIELD_FILLED_SUCCESS", "value_type": "checkbox"},
      {"field": "name", "state": "FIELD_SKIPPED_COMPLEX_HANDLED", "reason": "Covered by first_name + last_name"}
    ],
    "honeypots_detected": 0,
    "time_ms": 4200
  },

  "form_submission": {
    "state": "SUBMISSION_VERIFIED_SUCCESS",
    "method": "STANDARD_CLICK",
    "verification_method": "URL_CHANGE_VERIFICATION",
    "verification_confidence": 0.95,
    "blocker": null,
    "pre_url": "https://www.floydcdjr.com/contactus.aspx",
    "post_url": "https://www.floydcdjr.com/thank-you.aspx",
    "success_indicators": [
      "URL changed from /contactus.aspx to /thank-you.aspx",
      "HTTP redirect 302 observed"
    ],
    "time_ms": 1800,
    "screenshots": {
      "filled_form": "tests/floyd_cdjr_filled.png",
      "success_page": "tests/floyd_cdjr_success.png"
    }
  },

  "overall": {
    "status": "SUCCESS_COMPLETE",
    "category": "SUCCESS",
    "requires_manual_action": false,
    "manual_action_type": null,
    "total_time_ms": 12100,
    "steps_completed": [
      "CONTACT_PAGE_DISCOVERY",
      "FORM_DETECTION",
      "FIELD_IDENTIFICATION",
      "FORM_FILLING",
      "FORM_SUBMISSION"
    ],
    "failure_point": null,
    "confidence_score": 0.95,
    "retry_recommended": false,
    "notes": "Fully automated submission successful"
  }
}
```

### Failed - CAPTCHA Blocked
```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-10-03T18:50:15.456Z",

  "dealership": {
    "name": "ABC Chrysler",
    "website": "https://www.abcchrysler.com",
    "city": "Denver",
    "state": "CO"
  },

  "contact_page_discovery": {
    "state": "CONTACT_PAGE_FOUND",
    "method": "HOMEPAGE_LINK_ANALYSIS",
    "contact_url": "https://www.abcchrysler.com/contact/",
    "urls_attempted": 1,
    "cached": false,
    "time_ms": 2800
  },

  "form_detection": {
    "state": "FORM_DETECTED_VALID",
    "quality": "MEDIUM_QUALITY",
    "field_count": 5,
    "confidence_score": 1.0,
    "has_submit_button": true,
    "is_iframe": false,
    "platform": "wordpress",
    "time_ms": 1900
  },

  "field_identification": {
    "state": "FIELDS_IDENTIFIED",
    "total_fields": 6,
    "required_fields": ["name", "email", "phone", "message"],
    "optional_fields": [],
    "consent_fields": [],
    "honeypot_fields": [],
    "captcha_fields": ["g-recaptcha"],
    "time_ms": 400
  },

  "form_filling": {
    "state": "FORM_FILLED_COMPLETE",
    "fields_filled": 4,
    "fields_skipped": 2,
    "fill_rate": 0.67,
    "required_fill_rate": 1.0,
    "filling_details": [
      {"field": "name", "state": "FIELD_FILLED_SUCCESS"},
      {"field": "email", "state": "FIELD_FILLED_SUCCESS"},
      {"field": "phone", "state": "FIELD_FILLED_SUCCESS"},
      {"field": "message", "state": "FIELD_FILLED_SUCCESS"},
      {"field": "g-recaptcha", "state": "FIELD_SKIPPED_CAPTCHA", "reason": "CAPTCHA cannot be automated"}
    ],
    "honeypots_detected": 0,
    "time_ms": 3100
  },

  "form_submission": {
    "state": "SUBMISSION_FAILED_BLOCKER",
    "method": "NOT_ATTEMPTED",
    "verification_method": null,
    "verification_confidence": 0.0,
    "blocker": "CAPTCHA_DETECTED",
    "blocker_details": {
      "captcha_type": "reCAPTCHA_v2",
      "captcha_sitekey": "6LdxU..."
    },
    "time_ms": 0,
    "screenshots": {
      "filled_form": "tests/abc_chrysler_captcha.png"
    }
  },

  "overall": {
    "status": "BLOCKED_CAPTCHA",
    "category": "BLOCKED",
    "requires_manual_action": true,
    "manual_action_type": "SOLVE_CAPTCHA_AND_SUBMIT",
    "total_time_ms": 8200,
    "steps_completed": [
      "CONTACT_PAGE_DISCOVERY",
      "FORM_DETECTION",
      "FIELD_IDENTIFICATION",
      "FORM_FILLING"
    ],
    "failure_point": "FORM_SUBMISSION",
    "confidence_score": 0.0,
    "retry_recommended": false,
    "alternative_contact_methods": {
      "phone": "303-555-1234",
      "email": "sales@abcchrysler.com"
    },
    "notes": "Form filled but CAPTCHA prevents automated submission. Manual intervention required."
  }
}
```

### Failed - No Contact Form
```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2025-10-03T18:55:22.789Z",

  "dealership": {
    "name": "XYZ Motors",
    "website": "https://www.xyzmotors.com",
    "city": "Austin",
    "state": "TX"
  },

  "contact_page_discovery": {
    "state": "CONTACT_PAGE_FOUND",
    "method": "COMMON_PATTERN_MATCH",
    "contact_url": "https://www.xyzmotors.com/contact-us/",
    "urls_attempted": 2,
    "cached": false,
    "time_ms": 4500
  },

  "form_detection": {
    "state": "FORM_NOT_DETECTED",
    "quality": null,
    "field_count": 0,
    "confidence_score": 0.0,
    "has_submit_button": false,
    "is_iframe": false,
    "platform": "unknown",
    "page_content_type": "CONTACT_INFO_ONLY",
    "time_ms": 2500,
    "notes": "Page shows only phone and email, no form"
  },

  "field_identification": {
    "state": "NOT_APPLICABLE",
    "reason": "No form detected"
  },

  "form_filling": {
    "state": "NOT_APPLICABLE",
    "reason": "No form detected"
  },

  "form_submission": {
    "state": "SUBMISSION_NOT_ATTEMPTED",
    "reason": "No form available"
  },

  "overall": {
    "status": "FAILED_NO_FORM",
    "category": "FAILED",
    "requires_manual_action": true,
    "manual_action_type": "USE_ALTERNATIVE_CONTACT",
    "total_time_ms": 7000,
    "steps_completed": [
      "CONTACT_PAGE_DISCOVERY"
    ],
    "failure_point": "FORM_DETECTION",
    "confidence_score": 0.0,
    "retry_recommended": false,
    "alternative_contact_methods": {
      "phone": "512-555-5678",
      "email": "info@xyzmotors.com",
      "live_chat": true
    },
    "notes": "Contact page exists but has no form - only displays phone/email. Use alternative contact method."
  }
}
```

---

## Summary Dashboard View

### By Overall Status
```
SUCCESS_COMPLETE:          15/20  (75%)  ✅
SUCCESS_UNVERIFIED:         2/20  (10%)  ⚠️
PARTIAL_FORM_FILLED:        0/20  (0%)   ⚠️
BLOCKED_CAPTCHA:            1/20  (5%)   🔴
BLOCKED_TECHNICAL:          0/20  (0%)   🔴
FAILED_NO_FORM:             1/20  (5%)   🔴
FAILED_NO_CONTACT_PAGE:     1/20  (5%)   🔴
FAILED_SITE_ERROR:          0/20  (0%)   🔴
```

### By Step Success
```
CONTACT_PAGE_DISCOVERY:    18/20  (90%)
FORM_DETECTION:            17/20  (85%)
FIELD_IDENTIFICATION:      17/20  (85%)
FORM_FILLING:              17/20  (85%)
FORM_SUBMISSION:           15/20  (75%)
```

### Manual Actions Required
```
✅ NO ACTION NEEDED:        15/20  (75%)
⚠️  VERIFY SUBMISSION:       2/20  (10%)
🔴 SOLVE CAPTCHA:            1/20  (5%)
🔴 USE PHONE/EMAIL:          2/20  (10%)
```

---

## Implementation Notes

### Database Schema
```sql
CREATE TABLE submission_records (
  id UUID PRIMARY KEY,
  timestamp TIMESTAMP,

  -- Dealership
  dealer_name VARCHAR(255),
  dealer_website VARCHAR(255),
  dealer_city VARCHAR(100),
  dealer_state VARCHAR(2),

  -- Discovery
  discovery_state VARCHAR(50),
  discovery_method VARCHAR(50),
  contact_url TEXT,

  -- Detection
  detection_state VARCHAR(50),
  form_quality VARCHAR(20),
  field_count INT,
  confidence_score DECIMAL,

  -- Filling
  filling_state VARCHAR(50),
  fields_filled INT,
  fields_skipped INT,
  fill_rate DECIMAL,

  -- Submission
  submission_state VARCHAR(50),
  submission_method VARCHAR(50),
  verification_method VARCHAR(50),
  blocker VARCHAR(50),

  -- Overall
  overall_status VARCHAR(50) INDEX,
  requires_manual_action BOOLEAN INDEX,
  manual_action_type VARCHAR(50),
  total_time_ms INT,

  -- Full JSON
  full_record JSONB
);
```

### Query Examples
```sql
-- Get all requiring manual action
SELECT * FROM submission_records
WHERE requires_manual_action = TRUE
ORDER BY timestamp DESC;

-- Success rate by state
SELECT dealer_state,
  COUNT(*) as total,
  SUM(CASE WHEN overall_status = 'SUCCESS_COMPLETE' THEN 1 ELSE 0 END) as success,
  ROUND(SUM(CASE WHEN overall_status = 'SUCCESS_COMPLETE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate
FROM submission_records
GROUP BY dealer_state
ORDER BY success_rate DESC;

-- Most common blockers
SELECT blocker, COUNT(*) as count
FROM submission_records
WHERE blocker IS NOT NULL
GROUP BY blocker
ORDER BY count DESC;
```

---

This specification provides **clear, unambiguous states** for comprehensive tracking at every step of the automation process.
