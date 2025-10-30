"""Debug script to inspect phone field structure on David Stanley site"""

import asyncio
from enhanced_stealth_browser_config import create_enhanced_stealth_session

async def debug_phone_fields():
    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session(headless=False)

    try:
        print("Navigating to David Stanley Dodge...")
        await page.goto("https://www.davidstanleychryslerjeepdodgeofoklahoma.com/contact-us/",
                       wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        print("\n" + "="*80)
        print("ANALYZING PHONE FIELD STRUCTURE")
        print("="*80 + "\n")

        # Find all inputs near "Phone" label
        phone_info = await page.evaluate("""
            () => {
                const results = {
                    labels: [],
                    inputs: []
                };

                // Find phone labels
                const labels = Array.from(document.querySelectorAll('label, span, div, td'));
                for (const label of labels) {
                    const text = (label.textContent || '').trim();
                    if (text.toLowerCase() === 'phone' || text === 'Phone') {
                        results.labels.push({
                            tag: label.tagName,
                            text: text,
                            classes: Array.from(label.classList),
                            id: label.id || 'no-id'
                        });

                        // Find container
                        let container = label.closest('.form-group, .field, tr, td, div, li');
                        if (container) {
                            // Get all inputs in container
                            const inputs = Array.from(container.querySelectorAll('input'));
                            inputs.forEach((inp, idx) => {
                                const style = window.getComputedStyle(inp);
                                results.inputs.push({
                                    index: idx,
                                    type: inp.type,
                                    name: inp.name || 'no-name',
                                    id: inp.id || 'no-id',
                                    value: inp.value,
                                    placeholder: inp.placeholder || '',
                                    maxlength: inp.getAttribute('maxlength'),
                                    size: inp.getAttribute('size'),
                                    width: style.width,
                                    display: style.display,
                                    visibility: style.visibility
                                });
                            });
                        }
                    }
                }

                return results;
            }
        """)

        print(f"Found {len(phone_info['labels'])} phone labels:")
        for label in phone_info['labels']:
            print(f"  - {label['tag']}: '{label['text']}' (classes: {label['classes']}, id: {label['id']})")

        print(f"\nFound {len(phone_info['inputs'])} inputs in phone containers:")
        for inp in phone_info['inputs']:
            print(f"  [{inp['index']}] type={inp['type']}, name={inp['name']}, id={inp['id']}")
            print(f"      value='{inp['value']}', placeholder='{inp['placeholder']}'")
            print(f"      maxlength={inp['maxlength']}, size={inp['size']}, width={inp['width']}")
            print(f"      display={inp['display']}, visibility={inp['visibility']}")
            print()

        input("\nPress Enter to close browser...")

    finally:
        await browser.close()
        await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(debug_phone_fields())
