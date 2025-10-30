#!/usr/bin/env python3
"""
Hybrid Manual-Assisted Form Filler

This approach connects to your existing manual browser session to fill forms
without triggering Cloudflare detection.

WORKFLOW:
1. You manually navigate to a contact page in your regular Chrome
2. Run this script to connect to your existing browser
3. Script fills the form using your manual session
4. You manually review and submit, or script submits in human context

This bypasses Cloudflare fingerprint detection entirely.
"""

import asyncio
import json
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

class HybridManualFormFiller:
    """Form filler that connects to existing manual browser session."""

    def __init__(self):
        self.contact_data = {
            'first_name': 'Miguel',
            'last_name': 'Montoya',
            'email': 'migueljmontoya@protonmail.com',
            'phone': '555-123-4567',
            'zip': '90210',
            'message': 'I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals.'
        }

    async def connect_to_manual_browser(self):
        """Connect to existing Chrome browser with debugging enabled."""
        print("🔗 Attempting to connect to existing Chrome browser...")
        print("📋 SETUP INSTRUCTIONS:")
        print("   1. Close all Chrome windows")
        print("   2. Open Terminal and run:")
        print("      /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=\"/tmp/chrome-debug\"")
        print("   3. Navigate to a dealership contact page")
        print("   4. Press Enter here when ready...")

        input("Press Enter when you've completed the setup above...")

        try:
            playwright = await async_playwright().start()
            # Connect to existing browser
            browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts

            if not contexts:
                print("❌ No browser contexts found. Make sure Chrome is running with debugging enabled.")
                return None, None, None

            context = contexts[0]  # Use first context
            pages = context.pages

            if not pages:
                print("❌ No pages found. Make sure you have a page open.")
                return None, None, None

            page = pages[0]  # Use first page
            current_url = page.url

            print(f"✅ Connected to existing browser session")
            print(f"📄 Current page: {current_url}")

            return playwright, browser, page

        except Exception as e:
            print(f"❌ Failed to connect to browser: {e}")
            print("   Make sure Chrome is running with: --remote-debugging-port=9222")
            return None, None, None

    async def detect_and_fill_form(self, page):
        """Detect and fill form in the manual browser session."""

        print("\n🔍 Analyzing page for contact forms...")

        # Check if we're on a contact page
        page_content = await page.content()
        current_url = page.url

        if not any(word in current_url.lower() for word in ['contact', 'get-quote', 'inquiry']):
            print("⚠️  This doesn't appear to be a contact page.")
            print(f"   Current URL: {current_url}")
            print("   Please navigate to a contact page and try again.")
            return False

        # Look for form fields
        form_fields = {}

        # Common field selectors and their mappings
        field_mappings = {
            'first_name': [
                'input[name*="first"]', 'input[name*="fname"]', 'input[id*="first"]',
                'input[placeholder*="First"]', 'input[aria-label*="First"]'
            ],
            'last_name': [
                'input[name*="last"]', 'input[name*="lname"]', 'input[id*="last"]',
                'input[placeholder*="Last"]', 'input[aria-label*="Last"]'
            ],
            'email': [
                'input[type="email"]', 'input[name*="email"]', 'input[id*="email"]',
                'input[placeholder*="email"]', 'input[aria-label*="email"]'
            ],
            'phone': [
                'input[type="tel"]', 'input[name*="phone"]', 'input[id*="phone"]',
                'input[placeholder*="phone"]', 'input[aria-label*="phone"]'
            ],
            'zip': [
                'input[name*="zip"]', 'input[name*="postal"]', 'input[id*="zip"]',
                'input[placeholder*="zip"]', 'input[placeholder*="postal"]'
            ],
            'message': [
                'textarea', 'textarea[name*="message"]', 'textarea[name*="comment"]',
                'textarea[id*="message"]', 'textarea[placeholder*="message"]'
            ]
        }

        # Find fields
        for field_type, selectors in field_mappings.items():
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=1000):
                        form_fields[field_type] = selector
                        print(f"   ✅ Found {field_type}: {selector}")
                        break
                except:
                    continue

        if not form_fields:
            print("❌ No form fields detected on this page.")
            return False

        print(f"\n📝 Found {len(form_fields)} form fields. Beginning human-like filling...")

        # Fill fields with human-like behavior
        for field_type, selector in form_fields.items():
            if field_type in self.contact_data:
                try:
                    print(f"   Filling {field_type}...")

                    element = page.locator(selector).first

                    # Scroll field into view
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.5, 1.0))

                    # Click field
                    await element.click()
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                    # Clear existing content
                    await element.fill('')
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                    # Type with human-like speed
                    value = self.contact_data[field_type]
                    for char in value:
                        await page.keyboard.type(char)
                        await asyncio.sleep(random.uniform(0.05, 0.15))

                    print(f"   ✅ Filled {field_type}")

                    # Pause between fields (thinking time)
                    await asyncio.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"   ⚠️ Could not fill {field_type}: {e}")

        # Look for checkboxes
        print("\n☑️  Looking for consent checkboxes...")
        checkbox_selectors = [
            'input[type="checkbox"]',
            'input[name*="agree"]',
            'input[name*="consent"]',
            'input[id*="agree"]'
        ]

        checkboxes_checked = 0
        for selector in checkbox_selectors:
            try:
                checkboxes = page.locator(selector)
                count = await checkboxes.count()

                for i in range(count):
                    checkbox = checkboxes.nth(i)
                    if await checkbox.is_visible() and not await checkbox.is_checked():
                        # Get checkbox label/text to check if it's consent-related
                        label_text = ""
                        try:
                            # Try to find associated label
                            label = page.locator(f'label[for="{await checkbox.get_attribute("id")}"]').first
                            if await label.is_visible():
                                label_text = await label.text_content()
                        except:
                            pass

                        if any(word in label_text.lower() for word in ['agree', 'consent', 'privacy', 'terms']):
                            await checkbox.scroll_into_view_if_needed()
                            await asyncio.sleep(random.uniform(0.5, 1.0))
                            await checkbox.click()
                            checkboxes_checked += 1
                            print(f"   ✅ Checked consent checkbox: {label_text[:50]}...")
                            await asyncio.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                continue

        print(f"\n🎉 Form filling completed!")
        print(f"   📝 Fields filled: {len(form_fields)}")
        print(f"   ☑️  Checkboxes checked: {checkboxes_checked}")
        print(f"\n👤 NEXT STEPS:")
        print(f"   1. Review the filled form for accuracy")
        print(f"   2. Manually submit the form (recommended)")
        print(f"   3. OR type 'submit' to attempt automated submission")

        return True

    async def run_hybrid_session(self):
        """Run the hybrid manual-assisted form filling session."""

        print("🤖👤 HYBRID MANUAL-ASSISTED FORM FILLER")
        print("=" * 60)
        print("This tool fills forms in your existing manual browser session")
        print("to bypass Cloudflare detection completely.\n")

        # Connect to manual browser
        playwright, browser, page = await self.connect_to_manual_browser()

        if not page:
            return False

        try:
            # Fill the form
            success = await self.detect_and_fill_form(page)

            if success:
                print("\n" + "=" * 60)
                print("✅ HYBRID FORM FILLING COMPLETED SUCCESSFULLY!")
                print("   The form has been filled in your manual browser session.")
                print("   Since this uses your real browser, Cloudflare won't detect it.")
                print("   You can now manually submit or review the form.")

                # Ask if user wants automated submission
                submit_choice = input("\nType 'submit' to attempt automated submission (or Enter to skip): ").lower().strip()

                if submit_choice == 'submit':
                    print("\n🚀 Attempting automated submission...")
                    submit_selectors = [
                        'button[type="submit"]',
                        'input[type="submit"]',
                        'button:has-text("Submit")',
                        'button:has-text("Send")',
                        'button:has-text("Contact Us")'
                    ]

                    for selector in submit_selectors:
                        try:
                            submit_btn = page.locator(selector).first
                            if await submit_btn.is_visible(timeout=1000):
                                await submit_btn.scroll_into_view_if_needed()
                                await asyncio.sleep(1)
                                await submit_btn.click()
                                print("   ✅ Submit button clicked")

                                # Wait for response
                                await asyncio.sleep(3)

                                # Check for confirmation
                                page_content = await page.content()
                                if any(word in page_content.lower() for word in ['thank', 'confirm', 'success', 'received']):
                                    print("   🎉 Submission appears successful!")
                                elif 'blocked' in page_content.lower():
                                    print("   ⚠️ Submission was blocked")
                                else:
                                    print("   ❓ Submission result unclear")
                                break
                        except:
                            continue
                else:
                    print("   👤 Manual submission recommended for best results.")

            return success

        except Exception as e:
            print(f"❌ Error during form filling: {e}")
            return False

        finally:
            # Keep browser open (don't close the manual session)
            print("\n📌 Browser session remains open for your use.")


async def main():
    """Main function to run hybrid form filler."""

    filler = HybridManualFormFiller()

    print("🚀 Starting Hybrid Manual-Assisted Form Filling Session...")
    print("   This approach uses your real browser to bypass Cloudflare completely.\n")

    try:
        success = await filler.run_hybrid_session()

        if success:
            print("\n🎉 SESSION COMPLETED SUCCESSFULLY!")
            print("   Hybrid approach successfully filled form without detection.")
        else:
            print("\n⚠️ Session encountered issues.")
            print("   Check the instructions and try again.")

    except KeyboardInterrupt:
        print("\n⏹️ Session interrupted by user.")
    except Exception as e:
        print(f"\n💥 Session failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())