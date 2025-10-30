"""Debug script to inspect Jimmy Britt zip code field"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session
from src.automation.forms.enhanced_form_detector import EnhancedFormDetector
from src.automation.forms.complex_field_handler import ComplexFieldHandler

async def debug_jimmy_britt():
    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

    try:
        print("Navigating to Jimmy Britt Chrysler Jeep Dodge Ram...")
        await page.goto("https://www.jbchryslerjeepdodgeram.com/contact.htm",
                       wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        print("\n" + "="*80)
        print("ANALYZING ZIP CODE FIELD")
        print("="*80 + "\n")

        # Standard form detection
        form_detector = EnhancedFormDetector()
        form_result = await form_detector.detect_contact_form(page)

        print(f"Standard form detection found {len(form_result.fields)} fields:")
        for field_type, field_info in form_result.fields.items():
            print(f"  - {field_type}: {field_info.selector}")

        # Check for Gravity Forms zip
        complex_handler = ComplexFieldHandler()
        gravity_zip = await complex_handler.detect_gravity_forms_zip_code(page)

        if gravity_zip:
            print(f"\n✓ Gravity Forms zip detected")
        else:
            print(f"\n✗ Gravity Forms zip NOT detected")

        # Inspect all fields with "zip" or "postal" in the page
        print("\n" + "="*80)
        print("SEARCHING FOR ZIP/POSTAL FIELDS IN PAGE")
        print("="*80 + "\n")

        zip_info = await page.evaluate("""
            () => {
                const results = [];

                // Find all labels with "zip" or "postal" or "code"
                const labels = Array.from(document.querySelectorAll('label, span, div, td'));
                for (const label of labels) {
                    const text = (label.textContent || '').toLowerCase().trim();
                    if ((text.includes('zip') || text.includes('postal') || text.includes('code')) && text.length < 50) {
                        const forAttr = label.getAttribute('for');
                        let container = label.closest('.form-group, .field, .gfield, li, div, tr, td');

                        results.push({
                            labelText: label.textContent.trim(),
                            labelTag: label.tagName,
                            forAttribute: forAttr || 'none',
                            labelId: label.id || 'none',
                            labelClasses: Array.from(label.classList)
                        });

                        // Look for associated input
                        if (forAttr) {
                            const input = document.getElementById(forAttr);
                            if (input) {
                                results[results.length - 1].inputFound = true;
                                results[results.length - 1].inputId = input.id;
                                results[results.length - 1].inputName = input.name || 'none';
                                results[results.length - 1].inputType = input.type;
                            }
                        } else if (container) {
                            const inputs = container.querySelectorAll('input[type="text"], input[type="tel"], input:not([type])');
                            if (inputs.length > 0) {
                                const inp = inputs[0];
                                results[results.length - 1].inputFound = true;
                                results[results.length - 1].inputId = inp.id || 'none';
                                results[results.length - 1].inputName = inp.name || 'none';
                                results[results.length - 1].inputType = inp.type || 'text';
                            }
                        }
                    }
                }

                // Also find all inputs with zip/postal in name or id
                const inputs = Array.from(document.querySelectorAll('input'));
                for (const inp of inputs) {
                    const name = (inp.name || '').toLowerCase();
                    const id = (inp.id || '').toLowerCase();
                    const placeholder = (inp.placeholder || '').toLowerCase();

                    if (name.includes('zip') || name.includes('postal') ||
                        id.includes('zip') || id.includes('postal') ||
                        placeholder.includes('zip') || placeholder.includes('postal')) {
                        results.push({
                            foundBy: 'input search',
                            inputId: inp.id || 'none',
                            inputName: inp.name || 'none',
                            inputType: inp.type,
                            inputPlaceholder: inp.placeholder || 'none'
                        });
                    }
                }

                return results;
            }
        """)

        if zip_info:
            print(f"Found {len(zip_info)} potential zip code fields:\n")
            for idx, info in enumerate(zip_info, 1):
                print(f"Field #{idx}:")
                if 'labelText' in info:
                    print(f"  Label: '{info['labelText']}' ({info['labelTag']})")
                    print(f"  For attribute: {info.get('forAttribute', 'none')}")
                    print(f"  Label classes: {info.get('labelClasses', [])}")
                if 'inputFound' in info and info['inputFound']:
                    print(f"  ✓ Associated input found:")
                    print(f"    - ID: {info.get('inputId', 'none')}")
                    print(f"    - Name: {info.get('inputName', 'none')}")
                    print(f"    - Type: {info.get('inputType', 'none')}")
                elif 'foundBy' in info:
                    print(f"  Found by: {info['foundBy']}")
                    print(f"  - ID: {info.get('inputId', 'none')}")
                    print(f"  - Name: {info.get('inputName', 'none')}")
                    print(f"  - Type: {info.get('inputType', 'none')}")
                    print(f"  - Placeholder: {info.get('inputPlaceholder', 'none')}")
                print()
        else:
            print("No zip code fields found!")

        # Take screenshot
        await page.screenshot(path="tests/jimmy_britt_zipcode_debug.png", full_page=True)
        print("Screenshot saved: tests/jimmy_britt_zipcode_debug.png")

        input("\nPress Enter to close browser...")

    finally:
        await browser.close()
        await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(debug_jimmy_britt())
