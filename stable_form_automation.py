#!/usr/bin/env python3
"""
Stable Form Automation with Enhanced Overlay Handling

Simplified, stable version focused on reliable form submission with comprehensive
overlay removal and confirmation detection.
"""

import asyncio
import random
import sys
from pathlib import Path

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from playwright.async_api import async_playwright
from src.automation.forms.form_submitter import ContactPayload

class StableFormAutomation:
    """Stable form automation with comprehensive overlay handling."""

    def __init__(self):
        self.contact_data = ContactPayload(
            first_name="Miguel",
            last_name="Montoya",
            email="migueljmontoya@protonmail.com",
            phone="555-123-4567",
            zip_code="90210",
            message="I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals."
        )

    async def create_stable_browser(self):
        """Create stable browser without profile conflicts."""

        print("🚀 Launching stable browser...")

        playwright = await async_playwright().start()

        # Simple, stable browser launch
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        # Remove automation indicators
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)

        print("✅ Stable browser launched")
        return playwright, browser, page

    async def comprehensive_overlay_removal(self, page):
        """Remove ALL overlays, popups, and blocking elements."""

        print("🧹 Comprehensive overlay removal...")

        # Handle browser permissions
        context = page.context
        await context.grant_permissions([])

        overlay_count = 0

        # 1. Cookie consent (ACCEPT ALL)
        cookie_selectors = [
            '#onetrust-banner-sdk button[id*="accept"]',
            '#onetrust-banner-sdk button:has-text("Accept")',
            'button:has-text("Accept All Cookies")',
            'button:has-text("Accept Cookies")',
            'button:has-text("I Accept")',
            '[class*="cookie"] button:has-text("Accept")',
            '[class*="consent"] button:has-text("Accept")',
            '#accept-cookies', '#cookie-accept'
        ]

        for selector in cookie_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=2000):
                    await element.click()
                    overlay_count += 1
                    print(f"   🍪 ACCEPTED cookies")
                    await asyncio.sleep(1)
                    break
            except:
                continue

        # 2. Location permission (DENY)
        location_selectors = [
            'button:has-text("Block")', 'button:has-text("Don\'t Allow")',
            'button:has-text("Deny")', 'button:has-text("Never")',
            'button:has-text("Not Now")', 'button:has-text("No Thanks")'
        ]

        for selector in location_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    await element.click()
                    overlay_count += 1
                    print(f"   📍 DENIED location access")
                    await asyncio.sleep(0.5)
            except:
                continue

        # 3. Close unwanted popups
        popup_selectors = [
            '[class*="modal"] button:has-text("×")',
            '[class*="popup"] button:has-text("×")',
            '[class*="overlay"] button:has-text("Close")',
            '[class*="chat"] button:has-text("×")',
            'button[aria-label*="close" i]'
        ]

        for selector in popup_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(count):
                    element = elements.nth(i)
                    if await element.is_visible(timeout=1000):
                        await element.click()
                        overlay_count += 1
                        print(f"   ❌ CLOSED popup")
                        await asyncio.sleep(0.5)
            except:
                continue

        # 4. Aggressive JavaScript removal
        try:
            await page.evaluate("""
                // Remove all blocking overlays
                const removeElements = (selectors) => {
                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                            el.style.pointerEvents = 'none';
                            el.remove();
                        });
                    });
                };

                // Remove engagement and overlay elements
                removeElements([
                    '[id*="engagement"]', '[class*="engagement"]',
                    '[id*="layer"]', '[class*="layer"]',
                    '[id*="cover"]', '[class*="cover"]',
                    '[id*="modal"]', '[class*="modal"]',
                    '[id*="popup"]', '[class*="popup"]',
                    '[id*="overlay"]', '[class*="overlay"]',
                    '[id*="chat"]', '[class*="chat"]'
                ]);

                // Remove high z-index blocking elements
                const allElements = document.querySelectorAll('*');
                allElements.forEach(element => {
                    const styles = window.getComputedStyle(element);
                    const zIndex = parseInt(styles.zIndex);

                    if (zIndex > 500 && styles.position === 'fixed') {
                        const rect = element.getBoundingClientRect();
                        // If it covers significant screen area, it's likely blocking
                        if (rect.width > window.innerWidth * 0.5 || rect.height > window.innerHeight * 0.5) {
                            element.style.display = 'none';
                            element.remove();
                        }
                    }
                });

                console.log('Aggressive overlay cleanup completed');
            """)
            print(f"   🧹 JavaScript cleanup completed")
        except:
            pass

        if overlay_count > 0:
            print(f"   ✅ Removed {overlay_count} overlays total")

        return overlay_count

    async def detect_form_fields(self, page):
        """Detect form fields with honeypot protection."""

        print("🔍 Detecting form fields...")

        await page.wait_for_load_state("networkidle")

        # Comprehensive field patterns
        field_patterns = {
            'first_name': [
                'input[name*="first" i]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[id*="first" i]:not([style*="display: none"])',
                'input[placeholder*="first" i]:not([style*="display: none"])'
            ],
            'last_name': [
                'input[name*="last" i]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[id*="last" i]:not([style*="display: none"])',
                'input[placeholder*="last" i]:not([style*="display: none"])'
            ],
            'email': [
                'input[type="email"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="email" i]:not([style*="display: none"])'
            ],
            'phone': [
                'input[type="tel"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="phone" i]:not([style*="display: none"])'
            ],
            'zip': [
                'input[name*="zip" i]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="postal" i]:not([style*="display: none"])'
            ],
            'message': [
                'textarea:not([style*="display: none"]):not([style*="visibility: hidden"]):not([name*="honeypot"])',
                'textarea[name*="message" i]:not([style*="display: none"])'
            ]
        }

        detected_fields = {}

        for field_type, selectors in field_patterns.items():
            for selector in selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)

                        # Check if element is actually visible and not a honeypot
                        if (await element.is_visible() and
                            await element.is_enabled() and
                            not await self._is_honeypot(page, element)):

                            detected_fields[field_type] = element
                            print(f"   ✅ Found {field_type}")
                            break

                    if field_type in detected_fields:
                        break

                except:
                    continue

        # Find submit button
        submit_button = None
        submit_selectors = [
            'button[type="submit"]:not([style*="display: none"])',
            'input[type="submit"]:not([style*="display: none"])',
            'button:has-text("Submit"):not([style*="display: none"])',
            'button:has-text("Send"):not([style*="display: none"])',
            'button:has-text("Contact"):not([style*="display: none"])'
        ]

        for selector in submit_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()

                for i in range(count):
                    element = elements.nth(i)
                    if (await element.is_visible() and
                        not await self._is_honeypot(page, element)):
                        submit_button = element
                        print(f"   ✅ Found submit button")
                        break

                if submit_button:
                    break

            except:
                continue

        return detected_fields, submit_button

    async def _is_honeypot(self, page, element):
        """Check if element is a honeypot."""

        try:
            # Get element properties
            bounding_box = await element.bounding_box()
            if not bounding_box or bounding_box['width'] <= 1 or bounding_box['height'] <= 1:
                return True

            # Check CSS styles
            styles = await element.evaluate("""
                element => {
                    const computed = window.getComputedStyle(element);
                    return {
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        position: computed.position,
                        left: computed.left,
                        top: computed.top
                    };
                }
            """)

            # Hidden elements
            if (styles['display'] == 'none' or
                styles['visibility'] == 'hidden' or
                float(styles['opacity']) < 0.1):
                return True

            # Off-screen positioning
            left = styles['left']
            top = styles['top']
            if (left.startswith('-') or top.startswith('-') or
                'px' in left and float(left.replace('px', '')) < -100 or
                'px' in top and float(top.replace('px', '')) < -100):
                return True

            # Check for honeypot attributes
            attributes = await element.evaluate("""
                element => {
                    const attrs = {};
                    for (let attr of element.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)

            honeypot_keywords = ['honeypot', 'trap', 'bot', 'spam', 'hidden']
            for attr_name, attr_value in attributes.items():
                attr_text = f"{attr_name} {attr_value}".lower()
                if any(keyword in attr_text for keyword in honeypot_keywords):
                    return True

            return False

        except:
            return True

    async def fill_form_carefully(self, page, detected_fields):
        """Fill form with human-like behavior and overlay management."""

        print("📝 Filling form carefully...")

        # Remove overlays before filling
        await self.comprehensive_overlay_removal(page)

        filled_count = 0

        for field_type, element in detected_fields.items():
            if hasattr(self.contact_data, field_type):
                try:
                    print(f"   Filling {field_type}...")

                    # Ensure element is accessible
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.5, 1))

                    # Remove overlays again if needed
                    try:
                        await element.hover(timeout=3000)
                    except:
                        print(f"   🔧 Element blocked, clearing overlays...")
                        await self.comprehensive_overlay_removal(page)
                        await asyncio.sleep(1)

                    # Click and fill
                    await element.click()
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                    # Clear and type with human-like speed
                    await element.fill('')
                    value = getattr(self.contact_data, field_type)

                    for char in value:
                        await page.keyboard.type(char)
                        await asyncio.sleep(random.uniform(0.03, 0.1))

                    filled_count += 1
                    print(f"   ✅ Filled {field_type}")

                    # Human pause between fields
                    await asyncio.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"   ⚠️ Could not fill {field_type}: {e}")

        return filled_count

    async def submit_form_with_confirmation(self, page, submit_button):
        """Submit form and detect confirmation with enhanced detection."""

        print("🚀 Submitting form...")

        if not submit_button:
            print("   ❌ No submit button available")
            return False

        try:
            # Final overlay cleanup
            await self.comprehensive_overlay_removal(page)

            # Record initial state
            initial_url = page.url
            print(f"   📋 Initial URL: {initial_url}")

            # Ensure submit button is accessible
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(1)

            # Try to hover and click
            try:
                await submit_button.hover(timeout=3000)
                await asyncio.sleep(random.uniform(1, 2))
                await submit_button.click(timeout=3000)
                print("   ✅ Submit button clicked")
            except Exception as e:
                print(f"   ⚠️ Direct click failed, trying force click: {e}")
                await submit_button.click(force=True)
                print("   ✅ Submit button force-clicked")

            # Enhanced confirmation detection
            print("   ⏳ Waiting for submission confirmation...")

            # Multiple check phases with increasing delays
            for phase in range(3):
                await asyncio.sleep(random.uniform(2, 4))

                current_url = page.url
                page_content = await page.content()

                # Check for URL change indicating success
                if current_url != initial_url:
                    print(f"   🔄 URL changed to: {current_url}")
                    if any(word in current_url.lower() for word in ["thank", "success", "confirm", "complete"]):
                        print("   🎉 SUCCESS: Success URL detected!")
                        return True

                # Check for success messages
                success_patterns = [
                    "thank you", "thanks", "received", "submitted",
                    "confirmation", "success", "complete", "sent",
                    "message sent", "inquiry sent", "we'll be in touch",
                    "contact you soon", "received your message"
                ]

                if any(pattern in page_content.lower() for pattern in success_patterns):
                    print("   🎉 SUCCESS: Confirmation message detected!")
                    return True

                # Check for blocking
                if "blocked" in page_content.lower() or "cloudflare" in page_content.lower():
                    print("   ❌ BLOCKED: Security system blocked submission")
                    return False

                # Check for form errors
                error_patterns = ["error", "required", "invalid", "please enter"]
                if any(error in page_content.lower() for error in error_patterns):
                    print("   ⚠️ Form validation errors detected")
                    return False

                print(f"   ⏳ Checking phase {phase + 1}/3...")

            # Final assessment
            final_url = page.url
            final_content = await page.content()

            if final_url != initial_url:
                print("   ❓ URL changed but no clear success indicator")
                return "uncertain"
            else:
                print("   ❓ No clear submission result")
                return "uncertain"

        except Exception as e:
            print(f"   ❌ Submission failed: {e}")
            return False

    async def process_dealership(self, dealer_name, contact_url):
        """Process single dealership with stable automation."""

        print(f"\n🎯 Processing: {dealer_name}")
        print(f"🔗 URL: {contact_url}")
        print("=" * 60)

        playwright = None
        browser = None

        try:
            # Create stable browser
            playwright, browser, page = await self.create_stable_browser()

            # Navigate to target
            print("🧭 Navigating to contact page...")
            await page.goto(contact_url, wait_until="networkidle")

            # Comprehensive overlay removal
            await self.comprehensive_overlay_removal(page)

            # Detect form
            detected_fields, submit_button = await self.detect_form_fields(page)

            if not detected_fields:
                print("❌ No form fields detected")
                return False

            print(f"✅ Found {len(detected_fields)} fields")

            # Fill form
            filled_count = await self.fill_form_carefully(page, detected_fields)

            if filled_count == 0:
                print("❌ No fields were filled")
                return False

            print(f"✅ Filled {filled_count} fields")

            # Submit form
            result = await self.submit_form_with_confirmation(page, submit_button)

            if result is True:
                print("🎉 DEALERSHIP CONTACTED SUCCESSFULLY!")
                return True
            elif result == "uncertain":
                print("❓ Submission result uncertain")
                return "uncertain"
            else:
                print("❌ Submission failed")
                return False

        except Exception as e:
            print(f"💥 Error: {e}")
            return False

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()


async def test_stable_automation():
    """Test stable automation."""

    print("🛡️ STABLE FORM AUTOMATION TEST")
    print("🎯 Enhanced overlay handling and confirmation detection")
    print("=" * 70)

    automation = StableFormAutomation()

    # Test with Capital City CDJR
    result = await automation.process_dealership(
        dealer_name="Capital City CDJR (Stable Test)",
        contact_url="https://www.capcitycdjr.com/contact-us/"
    )

    print("\n" + "=" * 70)
    if result is True:
        print("🎉 STABLE AUTOMATION SUCCESSFUL!")
        print("   Form submitted successfully with confirmation!")
    elif result == "uncertain":
        print("❓ STABLE AUTOMATION UNCERTAIN")
        print("   Form may have been submitted - check email")
    else:
        print("❌ STABLE AUTOMATION FAILED")
        print("   Need further analysis")

    return result


if __name__ == "__main__":
    asyncio.run(test_stable_automation())