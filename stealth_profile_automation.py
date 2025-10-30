#!/usr/bin/env python3
"""
Stealth Profile Automation

Uses your actual Chrome Canary profile for large-scale automation with advanced evasion:
- Real user profile with browsing history, cookies, extensions
- Advanced stealth techniques to mask automation signatures
- Session warming and realistic browsing patterns
- Distributed timing to avoid pattern detection

This approach maintains the benefits of your real browser profile while enabling
full automation for large-scale dealership contacting.
"""

import asyncio
import random
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from playwright.async_api import async_playwright
from src.automation.forms.form_submitter import ContactPayload

class StealthProfileAutomation:
    """Full automation using real browser profile with advanced stealth."""

    def __init__(self, use_canary=True):
        self.use_canary = use_canary
        self.profile_path = self._get_profile_path()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.contact_data = ContactPayload(
            first_name="Miguel",
            last_name="Montoya",
            email="migueljmontoya@protonmail.com",
            phone="555-123-4567",
            zip_code="90210",
            message="I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals."
        )

    def _get_profile_path(self):
        """Get path to Chrome or Chrome Canary profile."""
        if self.use_canary:
            return "/Users/iliasbeshimov/Library/Application Support/Google/Chrome Canary"
        else:
            return "/Users/iliasbeshimov/Library/Application Support/Google/Chrome"

    def _create_isolated_profile(self):
        """Create isolated copy of profile for automation to avoid conflicts."""
        temp_dir = Path(tempfile.gettempdir()) / f"chrome_automation_{self.session_id}"
        temp_dir.mkdir(exist_ok=True)

        profile_copy = temp_dir / "profile"

        print(f"📁 Creating isolated profile copy...")
        print(f"   Source: {self.profile_path}")
        print(f"   Target: {profile_copy}")

        # Copy essential profile data (but not everything to avoid locks)
        essential_dirs = ["Default", "Local State"]

        if not profile_copy.exists():
            profile_copy.mkdir(parents=True)

        original_profile = Path(self.profile_path)

        for dir_name in essential_dirs:
            src = original_profile / dir_name
            dst = profile_copy / dir_name

            if src.exists():
                if src.is_file():
                    shutil.copy2(src, dst)
                elif src.is_dir():
                    try:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        print(f"   ✅ Copied {dir_name}")
                    except Exception as e:
                        print(f"   ⚠️ Could not copy {dir_name}: {e}")

        return str(profile_copy)

    async def create_stealth_browser(self):
        """Create browser with maximum stealth configuration."""

        # Use isolated profile copy
        profile_copy = self._create_isolated_profile()

        print("🕵️ Launching stealth browser with real profile...")

        playwright = await async_playwright().start()

        # Ultra-stealth launch arguments
        stealth_args = [
            # Remove automation indicators
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-dev-shm-usage",

            # Mimic normal browsing
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",

            # Performance and stability
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",

            # Remove distinctive fingerprints
            "--disable-features=VizDisplayCompositor,TranslateUI",
            "--disable-component-extensions-with-background-pages",
            "--disable-background-networking",

            # User agent and feature consistency
            "--enable-features=NetworkService,NetworkServiceLogging",
            "--force-color-profile=srgb",
            "--metrics-recording-only",

            # Additional stealth
            "--disable-client-side-phishing-detection",
            "--disable-sync",
            "--disable-background-mode",
        ]

        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=profile_copy,
            headless=False,  # Keep visible to appear more human
            args=stealth_args,
            ignore_default_args=["--enable-automation"],
            viewport={"width": 1366, "height": 768},  # Common resolution
            locale="en-US",
            timezone_id="America/Los_Angeles",
            geolocation={"latitude": 34.0522, "longitude": -118.2437},  # LA area
            permissions=["geolocation"]
        )

        # Create page with additional stealth
        page = await browser.new_page()

        # Remove automation artifacts
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Mock plugins and languages
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer'
                    }
                ]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Hide automation traces
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)

        print("✅ Stealth browser launched with real profile")
        return playwright, browser, page

    async def warm_up_session(self, page):
        """Warm up browser session with realistic browsing activity."""

        print("🔥 Warming up browser session...")

        warm_up_sites = [
            "https://www.google.com",
            "https://cars.com",
            "https://autotrader.com",
            "https://edmunds.com"
        ]

        for site in warm_up_sites[:2]:  # Visit 2 sites for warmup
            try:
                print(f"   Visiting {site}...")
                await page.goto(site, wait_until="networkidle")

                # Realistic browsing behavior
                await asyncio.sleep(random.uniform(2, 5))

                # Scroll around
                await page.evaluate(f"""
                    window.scrollTo(0, {random.randint(200, 800)});
                """)
                await asyncio.sleep(random.uniform(1, 3))

                # Maybe click a link
                if random.random() < 0.3:  # 30% chance
                    try:
                        links = page.locator('a[href]')
                        count = await links.count()
                        if count > 0:
                            link = links.nth(random.randint(0, min(count-1, 5)))
                            if await link.is_visible():
                                await link.click()
                                await asyncio.sleep(random.uniform(1, 2))
                    except:
                        pass

            except Exception as e:
                print(f"   ⚠️ Warmup site {site} failed: {e}")
                continue

        print("✅ Session warmup completed")

    async def navigate_like_human(self, page, target_url):
        """Navigate to target URL using human-like patterns."""

        print(f"🧭 Navigating to target: {target_url}")

        # Sometimes go via search (like a real user)
        if random.random() < 0.3:  # 30% chance
            print("   📍 Using search-based navigation...")

            await page.goto("https://www.google.com")
            await asyncio.sleep(random.uniform(1, 3))

            # Extract dealership name from URL for search
            from urllib.parse import urlparse
            domain = urlparse(target_url).netloc
            search_query = domain.replace('.com', '').replace('www.', '')

            # Search for dealership
            search_box = page.locator('input[name="q"]')
            await search_box.click()
            await asyncio.sleep(random.uniform(0.5, 1))

            # Type search with human-like speed
            for char in search_query:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))

            await page.keyboard.press('Enter')
            await asyncio.sleep(random.uniform(2, 4))

            # Try to click on a relevant result
            try:
                results = page.locator('a[href*="' + domain + '"]')
                if await results.count() > 0:
                    await results.first.click()
                    await asyncio.sleep(random.uniform(2, 4))
                else:
                    await page.goto(target_url, wait_until="networkidle")
            except:
                await page.goto(target_url, wait_until="networkidle")
        else:
            # Direct navigation
            await page.goto(target_url, wait_until="networkidle")

        await asyncio.sleep(random.uniform(2, 4))
        return page.url

    async def advanced_form_detection(self, page):
        """Enhanced form detection with honeypot filtering."""

        print("🔍 Detecting contact forms with honeypot protection...")

        # Wait for page to fully load
        await page.wait_for_load_state("networkidle")

        detected_fields = {}

        # Field detection with comprehensive selectors
        field_patterns = {
            'first_name': [
                'input[name*="first" i]', 'input[id*="first" i]', 'input[placeholder*="first" i]',
                'input[name="fname"]', 'input[name="firstname"]', 'input[name="first_name"]',
                'input[aria-label*="first" i]', 'input[class*="first" i]'
            ],
            'last_name': [
                'input[name*="last" i]', 'input[id*="last" i]', 'input[placeholder*="last" i]',
                'input[name="lname"]', 'input[name="lastname"]', 'input[name="last_name"]',
                'input[aria-label*="last" i]', 'input[class*="last" i]'
            ],
            'email': [
                'input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]',
                'input[placeholder*="email" i]', 'input[aria-label*="email" i]',
                'input[class*="email" i]'
            ],
            'phone': [
                'input[type="tel"]', 'input[name*="phone" i]', 'input[id*="phone" i]',
                'input[placeholder*="phone" i]', 'input[name*="tel" i]',
                'input[aria-label*="phone" i]', 'input[class*="phone" i]'
            ],
            'zip': [
                'input[name*="zip" i]', 'input[name*="postal" i]', 'input[id*="zip" i]',
                'input[placeholder*="zip" i]', 'input[name*="zipcode" i]',
                'input[aria-label*="zip" i]', 'input[class*="zip" i]'
            ],
            'message': [
                'textarea:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'textarea[name*="message" i]', 'textarea[name*="comment" i]',
                'textarea[id*="message" i]', 'textarea[placeholder*="message" i]',
                'textarea[aria-label*="message" i]', 'textarea[class*="message" i]',
                'input[type="text"][name*="message" i]'
            ]
        }

        for field_type, selectors in field_patterns.items():
            for selector in selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)

                        # CRITICAL: Advanced honeypot detection
                        if await self._is_honeypot_field(page, element):
                            print(f"   🍯 HONEYPOT DETECTED - Skipping {field_type}: {selector}")
                            continue

                        # Only use visible, interactable fields
                        if await element.is_visible() and await element.is_enabled():
                            detected_fields[field_type] = selector
                            print(f"   ✅ Found legitimate {field_type}: {selector}")
                            break

                    if field_type in detected_fields:
                        break

                except:
                    continue

        # Look for submit button (also check for honeypots)
        submit_selectors = [
            'button[type="submit"]', 'input[type="submit"]',
            'button:has-text("Submit")', 'button:has-text("Send")',
            'button:has-text("Contact")', 'button:has-text("Get Quote")',
            'button:has-text("Send Message")', 'button:has-text("Request Info")',
            'button:has-text("Get Started")', 'button:has-text("Continue")',
            'input[value*="Submit" i]', 'input[value*="Send" i]',
            '[class*="submit"]', '[id*="submit"]',
            'button', 'input[type="button"]'  # Fallback to any button
        ]

        submit_button = None
        for selector in submit_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()

                for i in range(count):
                    element = elements.nth(i)

                    # Check if submit button is visible and not honeypot
                    if await element.is_visible() and not await self._is_honeypot_field(page, element):
                        submit_button = selector
                        print(f"   ✅ Found legitimate submit button: {selector}")
                        break

                if submit_button:
                    break

            except:
                continue

        return detected_fields, submit_button

    async def _is_honeypot_field(self, page, element):
        """Advanced honeypot detection - only fill fields visible to users."""

        try:
            # Get element properties
            bounding_box = await element.bounding_box()

            # Check if element has zero size (common honeypot)
            if not bounding_box or bounding_box['width'] <= 1 or bounding_box['height'] <= 1:
                return True

            # Check CSS visibility properties
            styles = await element.evaluate('''
                element => {
                    const computed = window.getComputedStyle(element);
                    return {
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        position: computed.position,
                        left: computed.left,
                        top: computed.top,
                        width: computed.width,
                        height: computed.height,
                        zIndex: computed.zIndex,
                        overflow: computed.overflow
                    };
                }
            ''')

            # Hidden via CSS
            if (styles['display'] == 'none' or
                styles['visibility'] == 'hidden' or
                float(styles['opacity']) < 0.1):
                return True

            # Positioned off-screen (common honeypot technique)
            left = styles['left']
            top = styles['top']
            if (left.startswith('-') or top.startswith('-') or
                'px' in left and float(left.replace('px', '')) < -1000 or
                'px' in top and float(top.replace('px', '')) < -1000):
                return True

            # Extremely small size
            width = styles['width']
            height = styles['height']
            if ('px' in width and float(width.replace('px', '')) <= 1 or
                'px' in height and float(height.replace('px', '')) <= 1):
                return True

            # Check for honeypot keywords in attributes
            attributes = await element.evaluate('''
                element => {
                    const attrs = {};
                    for (let attr of element.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            ''')

            honeypot_keywords = [
                'honeypot', 'trap', 'bot', 'spam', 'hidden', 'invisible',
                'do-not-fill', 'leave-blank', 'email_confirm', 'website_url'
            ]

            for attr_name, attr_value in attributes.items():
                attr_text = f"{attr_name} {attr_value}".lower()
                if any(keyword in attr_text for keyword in honeypot_keywords):
                    return True

            # Check if element is covered by other elements (visibility trap)
            is_covered = await element.evaluate('''
                element => {
                    const rect = element.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const elementAtPoint = document.elementFromPoint(centerX, centerY);
                    return elementAtPoint !== element && !element.contains(elementAtPoint);
                }
            ''')

            if is_covered:
                return True

            return False

        except Exception as e:
            # If we can't determine, err on the side of caution
            print(f"   ⚠️ Could not check honeypot status: {e}")
            return True

    async def fill_form_stealthily(self, page, detected_fields):
        """Fill form with advanced human-like behavior."""

        print("📝 Filling form with stealth techniques...")

        # Handle popups and permissions first
        await self._handle_popups_and_permissions(page)

        filled_fields = []

        for field_type, selector in detected_fields.items():
            if hasattr(self.contact_data, field_type):
                try:
                    print(f"   Filling {field_type}...")

                    element = page.locator(selector).first

                    # Scroll into view naturally
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                    # Mouse hover before click (human behavior)
                    await element.hover()
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                    # Click field
                    await element.click()
                    await asyncio.sleep(random.uniform(0.2, 0.6))

                    # Clear and fill with human-like typing
                    await element.fill('')
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                    # Type with realistic speed and occasional pauses
                    value = getattr(self.contact_data, field_type)
                    for i, char in enumerate(value):
                        await page.keyboard.type(char)

                        # Realistic typing patterns
                        if char == ' ':
                            await asyncio.sleep(random.uniform(0.1, 0.3))
                        elif i > 0 and i % 8 == 0:  # Pause every 8 chars
                            await asyncio.sleep(random.uniform(0.1, 0.4))
                        else:
                            await asyncio.sleep(random.uniform(0.03, 0.12))

                    # Occasional "typo correction"
                    if random.random() < 0.15:  # 15% chance
                        await asyncio.sleep(random.uniform(0.2, 0.5))
                        await page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                        await page.keyboard.type(value[-1])  # Retype last char

                    filled_fields.append(field_type)
                    print(f"   ✅ Filled {field_type}")

                    # Human pause between fields
                    await asyncio.sleep(random.uniform(1.5, 4))

                except Exception as e:
                    print(f"   ⚠️ Could not fill {field_type}: {e}")

        # Handle checkboxes
        await self._handle_checkboxes(page)

        return filled_fields

    async def _handle_popups_and_permissions(self, page):
        """Comprehensive popup and permission handling."""

        print("🍪 Handling popups and permissions...")

        # Handle browser permissions proactively
        context = page.context

        # Accept cookies automatically, deny location access
        await context.grant_permissions([])  # Start with no permissions
        await context.set_geolocation(None)  # Disable geolocation

        # Handle cookie consent (ACCEPT ALL)
        cookie_selectors = [
            # OneTrust (very common)
            '#onetrust-banner-sdk button[id*="accept"]',
            '#onetrust-banner-sdk button:has-text("Accept All")',
            '#onetrust-banner-sdk button:has-text("Accept")',
            '#onetrust-banner-sdk button:has-text("I Accept")',

            # Generic cookie banners
            '[class*="cookie"] button:has-text("Accept All")',
            '[class*="cookie"] button:has-text("Accept")',
            '[class*="cookie"] button:has-text("I Accept")',
            '[class*="cookie"] button:has-text("Agree")',
            '[class*="cookie"] button:has-text("OK")',
            '[class*="cookie"] button:has-text("Continue")',

            # GDPR/Privacy consents
            '[class*="consent"] button:has-text("Accept All")',
            '[class*="consent"] button:has-text("Accept")',
            '[class*="privacy"] button:has-text("Accept")',
            '[class*="gdpr"] button:has-text("Accept")',

            # Common IDs
            '#accept-cookies', '#cookie-accept', '#cookieAccept',
            '#acceptAll', '#accept-all-cookies'
        ]

        cookies_handled = 0
        for selector in cookie_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=2000):
                    await element.click()
                    cookies_handled += 1
                    print(f"   🍪 ACCEPTED cookies: {selector}")
                    await asyncio.sleep(random.uniform(1, 2))
                    break  # Only click first matching cookie consent
            except:
                continue

        # Handle location permission popups (DENY/NEVER)
        location_selectors = [
            'button:has-text("Block")',
            'button:has-text("Don\'t Allow")',
            'button:has-text("Deny")',
            'button:has-text("Never")',
            'button:has-text("No Thanks")',
            'button:has-text("Not Now")',
            '[class*="location"] button:has-text("No")',
            '[class*="location"] button:has-text("Never")',
            '[class*="geolocation"] button:has-text("No")',
            '[class*="geolocation"] button:has-text("Never")',
            '[aria-label*="deny" i]',
            '[aria-label*="block" i]'
        ]

        location_handled = 0
        for selector in location_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    await element.click()
                    location_handled += 1
                    print(f"   📍 DENIED location: {selector}")
                    await asyncio.sleep(random.uniform(0.5, 1))
            except:
                continue

        # Handle annoying dealership popups (CLOSE)
        dealership_popup_selectors = [
            # Chat widgets
            '[class*="chat"] button:has-text("×")',
            '[class*="chat"] button:has-text("Close")',
            '[id*="chat"] button:has-text("×")',

            # Promotional popups
            '[class*="modal"] button:has-text("×")',
            '[class*="modal"] button:has-text("Close")',
            '[class*="popup"] button:has-text("×")',
            '[class*="popup"] button:has-text("Close")',
            '[class*="overlay"] button:has-text("×")',
            '[class*="overlay"] button:has-text("Close")',

            # "Special offers" / Newsletter popups
            '[class*="newsletter"] button:has-text("×")',
            '[class*="offer"] button:has-text("×")',
            '[class*="promotion"] button:has-text("×")',

            # Exit intent popups
            '[class*="exit"] button:has-text("×")',
            '[class*="exit"] button:has-text("No Thanks")',

            # Generic close buttons
            'button[aria-label*="close" i]',
            'button[title*="close" i]',
            '.close-button', '.btn-close'
        ]

        popups_closed = 0
        for selector in dealership_popup_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    await element.click()
                    popups_closed += 1
                    print(f"   ❌ CLOSED popup: {selector}")
                    await asyncio.sleep(random.uniform(0.5, 1))
            except:
                continue

        # JavaScript-based popup dismissal
        try:
            await page.evaluate("""
                // Close common modal patterns
                const modals = document.querySelectorAll('.modal, .popup, .overlay, [class*="modal"], [class*="popup"], [class*="overlay"]');
                modals.forEach(modal => {
                    if (modal.style.display !== 'none') {
                        modal.style.display = 'none';
                        modal.remove();
                    }
                });

                // Hide chat widgets and engagement containers
                const chats = document.querySelectorAll('[class*="chat"], [id*="chat"], [class*="messenger"], [id*="engagement"], [class*="engagement"]');
                chats.forEach(chat => {
                    chat.style.display = 'none';
                    chat.style.visibility = 'hidden';
                    chat.style.pointerEvents = 'none';
                    chat.remove();
                });

                // Remove specific interference elements
                const interferers = document.querySelectorAll('[id*="layer-cover"], [id*="engagement-container"], [class*="layer-cover"], [class*="engagement-container"]');
                interferers.forEach(element => {
                    element.style.display = 'none';
                    element.style.visibility = 'hidden';
                    element.style.pointerEvents = 'none';
                    element.remove();
                });

                // Hide sticky promotional elements
                const promotions = document.querySelectorAll('[class*="promotion"], [class*="offer"], [class*="banner"]:not([class*="cookie"])');
                promotions.forEach(promo => {
                    if (promo.style.position === 'fixed' || promo.style.position === 'sticky') {
                        promo.style.display = 'none';
                        promo.style.pointerEvents = 'none';
                    }
                });

                // Remove any elements with high z-index that might block interactions
                const allElements = document.querySelectorAll('*');
                allElements.forEach(element => {
                    const styles = window.getComputedStyle(element);
                    const zIndex = parseInt(styles.zIndex);
                    if (zIndex > 1000 && element.id.includes('engagement')) {
                        element.style.display = 'none';
                        element.remove();
                    }
                });
            """)
            print(f"   🧹 Enhanced overlay cleanup completed")
        except:
            pass

        total_handled = cookies_handled + location_handled + popups_closed
        if total_handled > 0:
            print(f"   ✅ Handled {total_handled} popups total")

        return total_handled

    async def _handle_checkboxes(self, page):
        """Handle consent checkboxes with honeypot detection."""

        print("☑️  Processing consent checkboxes...")

        checkbox_selectors = [
            'input[type="checkbox"]',
            'input[name*="agree" i]',
            'input[name*="consent" i]',
            'input[name*="terms" i]',
            'input[name*="privacy" i]'
        ]

        checkboxes_checked = 0

        for selector in checkbox_selectors:
            try:
                checkboxes = page.locator(selector)
                count = await checkboxes.count()

                for i in range(count):
                    checkbox = checkboxes.nth(i)

                    # Skip honeypot checkboxes
                    if await self._is_honeypot_field(page, checkbox):
                        print(f"   🍯 HONEYPOT checkbox detected - skipping")
                        continue

                    # Only check visible, unchecked, legitimate checkboxes
                    if (await checkbox.is_visible() and
                        await checkbox.is_enabled() and
                        not await checkbox.is_checked()):

                        # Get associated label text to understand what we're agreeing to
                        label_text = ""
                        try:
                            checkbox_id = await checkbox.get_attribute("id")
                            if checkbox_id:
                                label = page.locator(f'label[for="{checkbox_id}"]').first
                                if await label.is_visible():
                                    label_text = await label.text_content()
                        except:
                            pass

                        # Only check consent/agreement checkboxes, not subscriptions
                        if any(word in label_text.lower() for word in ['agree', 'consent', 'terms', 'privacy', 'policy']):
                            await checkbox.scroll_into_view_if_needed()
                            await asyncio.sleep(random.uniform(0.5, 1))

                            # Human-like checkbox interaction
                            await checkbox.hover()
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                            await checkbox.click()

                            checkboxes_checked += 1
                            print(f"   ✅ Checked consent checkbox: {label_text[:50]}...")
                            await asyncio.sleep(random.uniform(0.5, 1.5))

                        elif 'newsletter' in label_text.lower() or 'marketing' in label_text.lower():
                            print(f"   📧 SKIPPED newsletter checkbox: {label_text[:50]}...")

            except Exception as e:
                continue

        if checkboxes_checked > 0:
            print(f"   ✅ Checked {checkboxes_checked} consent checkboxes")

        return checkboxes_checked

    async def submit_form_naturally(self, page, submit_selector):
        """Submit form with human-like hesitation and enhanced confirmation detection."""

        print("🚀 Preparing to submit form...")

        if not submit_selector:
            print("   ❌ No submit button found")
            return False

        try:
            # Clear any remaining overlays before submission
            print("   🧹 Final overlay cleanup before submission...")
            await self._aggressive_overlay_removal(page)

            submit_button = page.locator(submit_selector).first

            # Ensure submit button is accessible
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(1, 2))

            # Check if submit button is still blocked
            try:
                await submit_button.hover(timeout=5000)
            except Exception as e:
                print(f"   🔧 Submit button blocked, trying aggressive cleanup...")
                await self._aggressive_overlay_removal(page)
                await asyncio.sleep(2)

            # Human-like hesitation sequence
            print("   🤔 Implementing human hesitation pattern...")

            # Hover over submit
            await submit_button.hover()
            await asyncio.sleep(random.uniform(1, 2))

            # Move away (like reviewing form)
            await page.mouse.move(random.randint(100, 300), random.randint(100, 300))
            await asyncio.sleep(random.uniform(1, 2))

            # Scroll up to review form quickly
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(random.uniform(1, 2))

            # Scroll back to submit
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(1, 2))

            # Final hover and submit
            await submit_button.hover()
            await asyncio.sleep(random.uniform(1, 2))

            # Record current URL before submission
            initial_url = page.url
            print(f"   📋 Initial URL: {initial_url}")

            print("   ✅ Clicking submit button...")
            await submit_button.click()

            # Enhanced submission confirmation detection
            return await self._detect_submission_confirmation(page, initial_url)

        except Exception as e:
            print(f"   ❌ Submission failed: {e}")
            return False

    async def _aggressive_overlay_removal(self, page):
        """Aggressive removal of all blocking elements."""

        try:
            await page.evaluate("""
                // Remove all high z-index elements
                const allElements = document.querySelectorAll('*');
                allElements.forEach(element => {
                    const styles = window.getComputedStyle(element);
                    const zIndex = parseInt(styles.zIndex);

                    // Remove high z-index blocking elements
                    if (zIndex > 100) {
                        const id = element.id || '';
                        const className = element.className || '';

                        if (id.includes('engagement') || id.includes('layer') || id.includes('cover') ||
                            className.includes('engagement') || className.includes('overlay') ||
                            className.includes('modal') || className.includes('popup') ||
                            styles.position === 'fixed' && zIndex > 500) {
                            element.style.display = 'none';
                            element.style.visibility = 'hidden';
                            element.style.pointerEvents = 'none';
                            element.remove();
                        }
                    }

                    // Also remove elements positioned over entire screen
                    if (styles.position === 'fixed' &&
                        styles.top === '0px' && styles.left === '0px' &&
                        (styles.width === '100%' || styles.width === '100vw')) {
                        if (!element.tagName.includes('FORM') && !element.closest('form')) {
                            element.style.display = 'none';
                            element.remove();
                        }
                    }
                });

                // Force remove specific known blocking patterns
                const blockingSelectors = [
                    '[id*="engagement"]', '[class*="engagement"]',
                    '[id*="layer-cover"]', '[class*="layer-cover"]',
                    '[id*="modal"]', '[class*="modal"]',
                    '[id*="popup"]', '[class*="popup"]',
                    '[id*="overlay"]', '[class*="overlay"]'
                ];

                blockingSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.pointerEvents = 'none';
                        el.remove();
                    });
                });
            """)
        except:
            pass

    async def _detect_submission_confirmation(self, page, initial_url):
        """Enhanced submission confirmation detection with proper delays."""

        print("   ⏳ Waiting for submission response...")

        # Phase 1: Immediate check (0-2 seconds)
        await asyncio.sleep(random.uniform(1, 2))

        # Phase 2: Short delay check (2-5 seconds)
        for i in range(3):
            await asyncio.sleep(random.uniform(1, 2))

            current_url = page.url
            page_content = await page.content()

            # Check for URL change
            if current_url != initial_url:
                print(f"   🔄 URL changed to: {current_url}")

                # URL change often indicates successful submission
                if any(word in current_url.lower() for word in ["thank", "success", "confirm", "complete"]):
                    print("   🎉 Success URL detected!")
                    return True

            # Check for success content
            success_indicators = [
                "thank you", "thanks", "received", "submitted", "confirmation",
                "success", "complete", "sent", "message sent", "inquiry sent",
                "we'll be in touch", "contact you soon", "received your message"
            ]

            if any(indicator in page_content.lower() for indicator in success_indicators):
                print("   🎉 Success message detected!")
                return True

            # Check for blocking
            if "blocked" in page_content.lower() or "cloudflare" in page_content.lower():
                print("   ❌ Submission blocked by security system")
                return False

            print(f"   ⏳ Checking submission status... ({i+1}/3)")

        # Phase 3: Extended wait for slower responses (5-10 seconds)
        print("   ⏳ Extended wait for submission confirmation...")

        for i in range(3):
            await asyncio.sleep(random.uniform(1.5, 2.5))

            current_url = page.url
            page_content = await page.content()

            # Re-check all indicators
            if current_url != initial_url and any(word in current_url.lower() for word in ["thank", "success", "confirm"]):
                print("   🎉 Success URL detected (delayed)!")
                return True

            success_indicators = [
                "thank you", "thanks", "received", "submitted", "confirmation",
                "success", "complete", "sent", "we'll be in touch"
            ]

            if any(indicator in page_content.lower() for indicator in success_indicators):
                print("   🎉 Success message detected (delayed)!")
                return True

            # Check for form validation errors
            error_indicators = ["error", "required", "invalid", "please enter", "field is required"]
            if any(error in page_content.lower() for error in error_indicators):
                print("   ⚠️ Form validation errors detected")
                return False

            print(f"   ⏳ Extended check... ({i+1}/3)")

        # Final assessment
        final_url = page.url
        final_content = await page.content()

        print(f"   📋 Final URL: {final_url}")

        if final_url != initial_url:
            print("   ❓ URL changed but no clear success indicator")
            return "uncertain"
        elif "blocked" in final_content.lower():
            print("   ❌ Final check shows blocking")
            return False
        else:
            print("   ❓ No clear submission result detected")
            return "uncertain"

    async def process_single_dealership(self, dealer_name, contact_url):
        """Process a single dealership with full stealth automation."""

        print(f"\n🎯 Processing: {dealer_name}")
        print(f"🔗 URL: {contact_url}")
        print("=" * 60)

        playwright = None
        browser = None

        try:
            # Create stealth browser
            playwright, browser, page = await self.create_stealth_browser()

            # Warm up session
            await self.warm_up_session(page)

            # Navigate like human
            final_url = await self.navigate_like_human(page, contact_url)

            # Handle initial popups after navigation
            await self._handle_popups_and_permissions(page)

            # Detect form
            detected_fields, submit_button = await self.advanced_form_detection(page)

            if not detected_fields:
                print("❌ No form fields detected")
                return False

            # Fill form
            filled_fields = await self.fill_form_stealthily(page, detected_fields)

            if not filled_fields:
                print("❌ No fields were filled")
                return False

            print(f"✅ Filled {len(filled_fields)} fields: {filled_fields}")

            # Submit form
            result = await self.submit_form_naturally(page, submit_button)

            if result is True:
                print("🎉 DEALERSHIP CONTACTED SUCCESSFULLY!")
                return True
            elif result == "uncertain":
                print("❓ Submission result unclear")
                return "uncertain"
            else:
                print("❌ Submission failed")
                return False

        except Exception as e:
            print(f"💥 Error processing dealership: {e}")
            return False

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

            # Clean up temp profile
            try:
                temp_dir = Path(tempfile.gettempdir()) / f"chrome_automation_{self.session_id}"
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except:
                pass


async def test_stealth_automation():
    """Test stealth automation on a single dealership."""

    print("🕵️ STEALTH PROFILE AUTOMATION TEST")
    print("🎯 Using real Chrome Canary profile with advanced evasion")
    print("=" * 70)

    automation = StealthProfileAutomation(use_canary=True)

    # Test with Capital City CDJR
    result = await automation.process_single_dealership(
        dealer_name="Capital City CDJR (Stealth Test)",
        contact_url="https://www.capcitycdjr.com/contact-us/"
    )

    print("\n" + "=" * 70)
    if result is True:
        print("🎉 STEALTH AUTOMATION SUCCESSFUL!")
        print("   Form submitted successfully using real profile")
    elif result == "uncertain":
        print("❓ STEALTH AUTOMATION UNCERTAIN")
        print("   Form may have been submitted - check email")
    else:
        print("❌ STEALTH AUTOMATION FAILED")
        print("   Need further refinement")

    return result


if __name__ == "__main__":
    asyncio.run(test_stealth_automation())