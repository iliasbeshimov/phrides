# Complex Field Handler - Quick Reference

## Import

```python
from src.automation.forms.complex_field_handler import ComplexFieldHandler
```

## Initialization

```python
complex_handler = ComplexFieldHandler()
```

## Detection Methods

### 1. Split Phone Field

```python
split_phone = await complex_handler.detect_split_phone_field(page)

# Returns: SplitPhoneField | None
# SplitPhoneField has:
#   - area_code: Locator
#   - prefix: Locator
#   - suffix: Locator
#   - area_code_selector: str
#   - prefix_selector: str
#   - suffix_selector: str
```

**Usage:**
```python
if split_phone:
    success = await complex_handler.fill_split_phone_field(split_phone, "6501234567")
```

### 2. Complex Name Field (Gravity Forms)

```python
complex_name = await complex_handler.detect_gravity_forms_complex_name(page)

# Returns: ComplexNameField | None
# ComplexNameField has:
#   - first_name: Locator
#   - last_name: Locator
#   - first_name_selector: str
#   - last_name_selector: str
```

**Usage:**
```python
if complex_name:
    success = await complex_handler.fill_complex_name_field(
        complex_name,
        "Miguel",
        "Montoya"
    )
```

### 3. Gravity Forms Zip Code

```python
gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)

# Returns: Locator | None
```

**Usage:**
```python
if gravity_zip:
    await gravity_zip.fill("94025")
```

## Complete Example

```python
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler

async def fill_contact_form(page, contact_data):
    # Standard detection
    form_detector = EnhancedFormDetector()
    form_result = await form_detector.detect_contact_form(page)

    if not form_result.success:
        return False

    # Complex field detection
    complex_handler = ComplexFieldHandler()

    split_phone = await complex_handler.detect_split_phone_field(page)
    complex_name = await complex_handler.detect_gravity_forms_complex_name(page)
    gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)

    # Fill complex fields
    if split_phone:
        await complex_handler.fill_split_phone_field(split_phone, contact_data['phone'])

    if complex_name:
        await complex_handler.fill_complex_name_field(
            complex_name,
            contact_data['first_name'],
            contact_data['last_name']
        )

    if gravity_zip:
        await gravity_zip.fill(contact_data['zip_code'])

    # Fill standard fields (skip those handled by complex handlers)
    for field_type, field_info in form_result.fields.items():
        if field_type == "phone" and split_phone:
            continue
        if field_type in ["first_name", "last_name"] and complex_name:
            continue
        if field_type == "zip" and gravity_zip:
            continue

        value = contact_data.get(field_type)
        if value:
            await field_info.element.fill(value)

    return True
```

## Phone Number Formats Supported

- `"1234567890"` - 10 digits
- `"11234567890"` - 11 digits (leading 1 stripped)
- `"(123) 456-7890"` - Formatted (non-digits stripped)
- `"123-456-7890"` - Dashed (non-digits stripped)

Split into:
- Area code: first 3 digits
- Prefix: next 3 digits
- Suffix: last 4 digits

## Error Handling

All methods return `None` on failure and log debug messages. Check return values:

```python
split_phone = await complex_handler.detect_split_phone_field(page)
if split_phone:
    success = await complex_handler.fill_split_phone_field(split_phone, phone)
    if not success:
        logger.warning("Failed to fill split phone field")
```

## Detected Patterns

### Split Phone
- Container with "phone" or "telephone" label
- 3 consecutive text/tel inputs
- Maxlength attributes: 3, 3, 4 (or similar)

### Complex Name
- Gravity Forms: `.gfield--type-name` class
- Generic: "Name" label → 2 inputs with "First"/"Last" sub-labels

### Gravity Zip
- Label with "Zip Code" or "Zip Code*" text
- Associated text input (via `for` attribute or parent container)
