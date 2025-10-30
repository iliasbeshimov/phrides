# Complex Field Detection Fixes - Implementation Summary

**Date:** September 30, 2025
**Issues Addressed:** 3 dealership form detection failures from `fixed_test_20250930_130207`

## Problems Identified

From the latest test results, three dealerships had special field patterns that our standard form detector couldn't handle:

1. **David Stanley Dodge LLC** (`davidstanleychryslerjeepdodgeofoklahoma.com/contact-us/`)
   - **Issue:** Phone number split across 3 separate text boxes (area code, prefix, suffix)
   - **Pattern:** `___` - `___` - `____` (3 digits, 3 digits, 4 digits)

2. **Faws Garage** (`fawsgaragecdjr.com/contact-us/`)
   - **Issue:** Phone number split across 3 separate text boxes
   - **Same pattern as above**

3. **Fillback Chrysler, Dodge, Jeep & Ram** (`fillbackprairieduchiencdjr.com/contact-us/`)
   - **Issue:** Gravity Forms with complex name field structure
   - **Pattern:**
     - Parent label: "Name*"
     - Two child inputs with sub-labels: "First" and "Last"
     - Zip Code field not detected by standard selectors
     - HTML: `input[name="input_10.3"]` for first name, `input[name="input_10.6"]` for last name

## Solution Implemented

### New Module: `src/automation/forms/complex_field_handler.py`

Created a specialized handler for complex field patterns with the following capabilities:

#### 1. Split Phone Number Detection (`detect_split_phone_field`)

**How it works:**
- Searches for labels containing "phone" or "telephone"
- Looks for 3 consecutive text inputs within the container
- Validates inputs have appropriate `maxlength` attributes (3, 3, 4)
- Returns `SplitPhoneField` dataclass with locators for all three inputs

**Filling logic (`fill_split_phone_field`):**
- Accepts phone formats: "1234567890", "(123) 456-7890", "123-456-7890"
- Strips all non-digits
- Handles 10-digit and 11-digit (with leading '1') numbers
- Splits into: area code [0:3], prefix [3:6], suffix [6:10]
- Fills each field with proper delays (0.2s between fields)

#### 2. Complex Name Field Detection (`detect_gravity_forms_complex_name`)

**Pattern matching:**
- Detects Gravity Forms `.gfield--type-name` containers
- Looks for `.name_first` and `.name_last` child containers
- Falls back to generic pattern: "Name" label → container → 2 inputs with "First"/"Last" sub-labels
- Returns `ComplexNameField` dataclass

**Filling logic (`fill_complex_name_field`):**
- Fills first name input
- 0.2s delay
- Fills last name input

#### 3. Gravity Forms Zip Code Detection (`detect_gravity_forms_zip_code`)

**Enhanced detection:**
- Searches for labels with exact text "Zip Code" or "Zip Code*"
- Follows `for` attribute to linked input
- Falls back to searching parent container for text input
- Specifically designed for Gravity Forms `input[name="input_9"]` pattern

### Data Structures

```python
@dataclass
class SplitPhoneField:
    area_code: Locator
    prefix: Locator
    suffix: Locator
    area_code_selector: str
    prefix_selector: str
    suffix_selector: str

@dataclass
class ComplexNameField:
    first_name: Locator
    last_name: Locator
    first_name_selector: str
    last_name_selector: str
```

## Integration Strategy

### Usage Pattern

```python
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler

# Detect standard form first
form_detector = EnhancedFormDetector()
form_result = await form_detector.detect_contact_form(page)

# Check for complex field patterns
complex_handler = ComplexFieldHandler()

# Check for split phone
split_phone = await complex_handler.detect_split_phone_field(page)
if split_phone:
    await complex_handler.fill_split_phone_field(split_phone, "6501234567")

# Check for complex name
complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
if complex_name:
    await complex_handler.fill_complex_name_field(complex_name, "Miguel", "Montoya")

# Check for Gravity Forms zip
gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)
if gravity_zip:
    await gravity_zip.fill("94025")

# Fill remaining standard fields
for field_type, field_info in form_result.fields.items():
    # Skip fields already handled by complex handlers
    if field_type == "phone" and split_phone:
        continue
    if field_type in ["first_name", "last_name"] and complex_name:
        continue
    if field_type == "zip" and gravity_zip:
        continue

    # Fill normally
    await field_info.element.fill(value)
```

## Test Script

Created `test_complex_field_fixes.py` to validate fixes on the 3 problem dealerships:

**Features:**
- Tests all 3 dealerships with their specific issues
- Detects and fills both standard and complex fields
- Takes screenshots for visual validation
- Logs detailed information about field detection
- Saves results to `tests/complex_field_test/`

**Test Data:**
```python
{
    "first_name": "Miguel",
    "last_name": "Montoya",
    "email": "miguelpmontoya@protonmail.com",
    "phone": "6501234567",
    "zip_code": "94025",
    "message": "Hi, I am interested in leasing a new SUV..."
}
```

## JavaScript Detection Logic

### Split Phone Pattern (Browser-Side)

The handler uses JavaScript to find phone field containers:

```javascript
const containers = [];
const labels = Array.from(document.querySelectorAll('label, div, span'));

for (const label of labels) {
    const text = (label.textContent || '').toLowerCase();
    if (text.includes('phone') || text.includes('telephone')) {
        let container = label.closest('.form-group, .field, .gfield, li, div');
        if (container) {
            const inputs = Array.from(container.querySelectorAll('input[type="text"], input[type="tel"]'));
            if (inputs.length === 3) {
                // Check maxlength attributes
                const maxLengths = inputs.map(i => i.getAttribute('maxlength'));
                if (maxLengths.filter(m => m === '3' || m === '4').length >= 2) {
                    // Found split phone field!
                    containers.push({
                        areaCode: inputs[0].id || inputs[0].name,
                        prefix: inputs[1].id || inputs[1].name,
                        suffix: inputs[2].id || inputs[2].name
                    });
                }
            }
        }
    }
}
```

### Gravity Forms Name Pattern

```javascript
// Look for Gravity Forms name field containers
const nameContainers = document.querySelectorAll('.gfield--type-name, [class*="name_"]');

for (const container of nameContainers) {
    const firstInput = container.querySelector('.name_first input, input[id*="_3"]');
    const lastInput = container.querySelector('.name_last input, input[id*="_6"]');

    if (firstInput && lastInput) {
        // Found complex name field!
    }
}
```

## Expected Improvements

### Before (from latest test):
- **David Stanley Dodge LLC:** Form detected ✓, Phone filled ✓ (but as single field - WRONG)
- **Faws Garage:** Form detected ✓, Phone filled ✓ (but as single field - WRONG)
- **Fillback Chrysler:** Form detected ✓, Missing first_name, last_name, zip_code ✗

### After (with complex field handler):
- **David Stanley Dodge LLC:** Form detected ✓, Split phone detected ✓, All 3 phone inputs filled ✓
- **Faws Garage:** Form detected ✓, Split phone detected ✓, All 3 phone inputs filled ✓
- **Fillback Chrysler:** Form detected ✓, Complex name detected ✓, First/Last filled ✓, Zip filled ✓

## Next Steps

### 1. Integration into Main Automation Scripts

Update `final_retest_with_contact_urls.py` to use complex field handler:

```python
# Add after standard form detection
complex_handler = ComplexFieldHandler()

# Detect complex fields
split_phone = await complex_handler.detect_split_phone_field(page)
complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)

# Fill complex fields first
if split_phone:
    await complex_handler.fill_split_phone_field(split_phone, contact_data['phone'])
    fields_filled.append("phone_split")

if complex_name:
    await complex_handler.fill_complex_name_field(
        complex_name,
        contact_data['first_name'],
        contact_data['last_name']
    )
    fields_filled.extend(["first_name_complex", "last_name_complex"])

if gravity_zip:
    await gravity_zip.fill(contact_data['zip_code'])
    fields_filled.append("zip_gravity")
```

### 2. Run Full Validation

Test on all 20 dealerships from latest test:

```bash
python final_retest_with_contact_urls.py --with-complex-fields
```

### 3. Additional Pattern Detection

Consider adding detection for:
- Date of birth split fields (MM/DD/YYYY)
- Address split fields (street, city, state, zip)
- Credit card input patterns
- Other Gravity Forms complex fields (address, time, etc.)

### 4. Performance Metrics

Track how many sites benefit from complex field detection:
- Percentage using split phone fields
- Percentage using Gravity Forms complex structures
- Overall improvement in field fill success rate

## Files Created/Modified

### New Files:
1. `src/automation/forms/complex_field_handler.py` - Main handler (360 lines)
2. `test_complex_field_fixes.py` - Test script (240 lines)
3. `COMPLEX_FIELD_FIXES_SUMMARY.md` - This document

### Dependencies:
- `playwright.async_api` - For browser automation
- `src.utils.logging` - For structured logging
- `enhanced_stealth_browser_config` - For browser session management
- `src.automation.forms.enhanced_form_detector` - For standard form detection

## Logging Examples

Successful split phone detection:
```
[INFO] Detected split phone field | {"operation": "split_phone_detected", "area_code": "#phone_area", "prefix": "#phone_prefix", "suffix": "#phone_suffix"}
[INFO] Filled split phone field | {"operation": "split_phone_filled", "area_code": "650", "prefix": "123", "suffix": "4567"}
```

Successful complex name detection:
```
[INFO] Detected Gravity Forms complex name field | {"operation": "complex_name_detected", "first_name": "#input_1_10_3", "last_name": "#input_1_10_6"}
[INFO] Filled complex name field | {"operation": "complex_name_filled", "first_name": "Miguel", "last_name": "Montoya"}
```

## Conclusion

The complex field handler provides robust detection and filling for non-standard form patterns that traditional selectors miss. By using JavaScript-based structural analysis, it can identify patterns like:

- Multi-input phone fields
- Gravity Forms complex name structures with sub-labels
- Label-based field detection when IDs/names are generic

This should improve the overall success rate from 85% to 90%+ by correctly handling these edge cases.
