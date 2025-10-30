#!/usr/bin/env python3
"""
Ultimate Dealership Automation for Residential IP

This implementation combines all successful techniques with advanced strategies
specifically designed for single residential IP operation:

1. Session persistence and rotation
2. Advanced timing distribution
3. Browser fingerprint randomization
4. Comprehensive evasion techniques
5. Smart submission strategies

Designed to maximize success rate while avoiding detection patterns.
"""

import asyncio
import random
import sys
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project paths
ROOT = Path(__file__).resolve().parent
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from playwright.async_api import async_playwright
from src.automation.forms.form_submitter import ContactPayload

class UltimateDealershipAutomation:
    """Ultimate automation system optimized for residential IP operation."""

    def __init__(self):
        self.contact_data = ContactPayload(
            first_name="Miguel",
            last_name="Montoya",
            email="migueljmontoya@protonmail.com",
            phone="555-123-4567",
            zip_code="90210",
            message="I am interested in learning more about your vehicle inventory and leasing options. Please contact me with available deals."
        )

        # Session management
        self.session_start_time = datetime.now()
        self.submissions_count = 0
        self.last_submission_time = None

        # Success tracking
        self.success_rate = []
        self.recent_blocks = []

    def calculate_smart_delay(self) -> float:
        """Calculate intelligent delay based on recent activity and success patterns."""

        base_delay = random.uniform(60, 180)  # 1-3 minutes base

        # Increase delay if we've had recent blocks
        recent_blocks = [t for t in self.recent_blocks if (datetime.now() - t).seconds < 1800]  # 30 min
        if recent_blocks:
            block_penalty = len(recent_blocks) * 120  # 2 min per recent block
            base_delay += block_penalty

        # Increase delay as session progresses
        session_duration = (datetime.now() - self.session_start_time).seconds
        if session_duration > 3600:  # After 1 hour
            base_delay += random.uniform(300, 600)  # Add 5-10 minutes

        # Time-of-day adjustments (peak hours = more delay)
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            base_delay += random.uniform(60, 120)
        elif 18 <= current_hour <= 21:  # Evening
            base_delay += random.uniform(30, 90)

        return base_delay

    async def create_advanced_stealth_browser(self):
        """Create browser with maximum stealth and fingerprint randomization."""

        print("🕵️ Creating advanced stealth browser...")

        playwright = await async_playwright().start()

        # Randomize viewport to avoid fingerprinting
        viewports = [
            {'width': 1366, 'height': 768},
            {'width': 1920, 'height': 1080},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864}
        ]
        viewport = random.choice(viewports)

        # Randomize user agent slightly
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        user_agent = random.choice(user_agents)

        # Advanced stealth arguments
        stealth_args = [
            '--disable-blink-features=AutomationControlled',
            '--exclude-switches=enable-automation',
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=VizDisplayCompositor,TranslateUI',
            '--disable-component-extensions-with-background-pages',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-default-browser-check',
            '--no-pings',
            '--no-default-browser-check',
            '--disable-client-side-phishing-detection',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-domain-reliability',
            '--disable-background-mode'
        ]

        browser = await playwright.chromium.launch(
            headless=False,
            args=stealth_args
        )

        context = await browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale='en-US',
            timezone_id='America/Los_Angeles',
            permissions=[],  # Start with no permissions
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        )

        page = await context.new_page()

        # Advanced stealth injection
        await page.add_init_script("""
            // Remove webdriver traces
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Mock plugins realistically
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: 'Chrome PDF Plugin',
                        description: 'Portable Document Format',
                        filename: 'internal-pdf-viewer',
                        length: 1
                    },
                    {
                        name: 'Chrome PDF Viewer',
                        description: 'Chrome PDF Viewer',
                        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                        length: 1
                    }
                ]
            });

            // Mock languages array
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Mock hardwareConcurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });

            // Mock deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });

            // Remove automation artifacts
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

            // Mock permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: 'default' }) :
                    originalQuery(parameters)
            );

            // Add realistic timing to make interactions less detectable
            const originalAddEventListener = EventTarget.prototype.addEventListener;
            EventTarget.prototype.addEventListener = function(type, listener, options) {
                if (type === 'click' || type === 'mousedown' || type === 'mouseup') {
                    const wrappedListener = function(event) {
                        // Add small random delay to make clicks less robotic
                        setTimeout(() => listener.call(this, event), Math.random() * 5);
                    };
                    return originalAddEventListener.call(this, type, wrappedListener, options);
                }
                return originalAddEventListener.call(this, type, listener, options);
            };
        """)

        print("✅ Advanced stealth browser created")
        return playwright, browser, page

    async def intelligent_session_warmup(self, page):
        """Intelligent session warmup that establishes browsing context."""

        print("🔥 Intelligent session warmup...")

        # Phase 1: Establish browsing context
        warmup_sequence = [
            "https://www.google.com",
            "https://cars.com",
            "https://autotrader.com"
        ]

        for i, site in enumerate(warmup_sequence[:2]):  # Limit to 2 sites
            try:
                print(f"   🌐 Visiting {site}...")
                await page.goto(site, wait_until="networkidle", timeout=30000)

                # Human-like browsing behavior
                await asyncio.sleep(random.uniform(2, 5))

                # Realistic scrolling
                scroll_distance = random.randint(300, 1000)
                await page.evaluate(f"window.scrollTo(0, {scroll_distance})")
                await asyncio.sleep(random.uniform(1, 3))

                # Sometimes interact with elements (but don't trigger navigation)
                if random.random() < 0.3:
                    try:
                        # Find safe elements to hover (non-navigating)
                        safe_elements = await page.locator('div, span, p, h1, h2, h3').all()
                        if safe_elements:
                            element = random.choice(safe_elements[:5])
                            await element.hover(timeout=2000)
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass

                # Variable timing between sites
                if i < len(warmup_sequence) - 1:
                    await asyncio.sleep(random.uniform(3, 8))

            except Exception as e:
                print(f"   ⚠️ Warmup site {site} had issues: {e}")
                continue

        print("✅ Session warmup completed")

    async def comprehensive_stealth_navigation(self, page, target_url):
        """Navigate to target with maximum stealth."""

        print(f"🧭 Stealth navigation to: {target_url}")

        # Sometimes use search-based navigation (more human-like)
        if random.random() < 0.4:  # 40% chance
            print("   🔍 Using search-based navigation...")

            try:
                # Go to Google if not already there
                if 'google.com' not in page.url:
                    await page.goto("https://www.google.com", wait_until="networkidle")
                    await asyncio.sleep(random.uniform(1, 3))

                # Extract dealership name for search
                from urllib.parse import urlparse
                domain = urlparse(target_url).netloc
                search_term = domain.replace('.com', '').replace('www.', '').replace('-', ' ')

                # Search with human typing
                search_box = page.locator('input[name="q"], input[title="Search"]').first
                await search_box.click()
                await asyncio.sleep(random.uniform(0.5, 1))

                # Type with realistic speed
                for char in search_term:
                    await page.keyboard.type(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))

                await asyncio.sleep(random.uniform(0.5, 1.5))
                await page.keyboard.press('Enter')
                await asyncio.sleep(random.uniform(3, 6))

                # Try to find and click relevant result
                try:
                    results = page.locator(f'a[href*="{domain}"]')
                    if await results.count() > 0:
                        result = results.first
                        await result.click()
                        await asyncio.sleep(random.uniform(3, 6))
                        print("   ✅ Clicked search result")
                    else:
                        # Fallback to direct navigation
                        await page.goto(target_url, wait_until="networkidle")
                except:
                    await page.goto(target_url, wait_until="networkidle")

            except Exception as e:
                print(f"   ⚠️ Search navigation failed: {e}, using direct")
                await page.goto(target_url, wait_until="networkidle")
        else:
            # Direct navigation with human timing
            await page.goto(target_url, wait_until="networkidle")

        await asyncio.sleep(random.uniform(2, 4))
        return page.url

    async def ultimate_overlay_management(self, page):
        """Ultimate overlay and popup management system."""

        print("🛡️ Ultimate overlay management...")

        overlays_handled = 0

        # Phase 1: Handle browser-level permissions
        context = page.context
        await context.grant_permissions([])  # No permissions by default

        # Phase 2: Cookie consent (ALWAYS ACCEPT)
        cookie_selectors = [
            # OneTrust patterns
            '#onetrust-banner-sdk button[id*="accept"]',
            '#onetrust-banner-sdk button:has-text("Accept All")',
            '#onetrust-banner-sdk button:has-text("Accept")',
            '#onetrust-banner-sdk button:has-text("I Accept")',
            '#onetrust-banner-sdk .ot-pc-refuse-all-handler',

            # Generic patterns
            'button:has-text("Accept All Cookies")',
            'button:has-text("Accept Cookies")',
            'button:has-text("Accept All")',
            'button:has-text("I Accept")',
            'button:has-text("Accept and Continue")',
            '[class*="cookie"] button:has-text("Accept")',
            '[class*="consent"] button:has-text("Accept")',

            # Common IDs
            '#accept-cookies', '#cookie-accept', '#acceptAll',
            '#cookie-consent-accept', '#cookieConsentAccept'
        ]

        for selector in cookie_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=3000):
                    await element.click()
                    overlays_handled += 1
                    print(f"   🍪 ACCEPTED cookies")
                    await asyncio.sleep(random.uniform(1, 2))
                    break  # Only click first matching consent
            except:
                continue

        # Phase 3: Location permissions (ALWAYS DENY)
        location_selectors = [
            'button:has-text("Block")',
            'button:has-text("Don\'t Allow")',
            'button:has-text("Deny")',
            'button:has-text("Never")',
            'button:has-text("Not Now")',
            'button:has-text("No Thanks")',
            'button:has-text("Decline")',
            '[aria-label*="deny" i]',
            '[aria-label*="block" i]'
        ]

        for selector in location_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(min(count, 3)):  # Max 3 location denials
                    element = elements.nth(i)
                    if await element.is_visible(timeout=2000):
                        await element.click()
                        overlays_handled += 1
                        print(f"   📍 DENIED location access")
                        await asyncio.sleep(random.uniform(0.5, 1))
            except:
                continue

        # Phase 4: Close promotional popups
        popup_close_selectors = [
            # Chat widgets
            '[class*="chat"] button:has-text("×")',
            '[class*="chat"] .close',
            '[id*="chat"] button:has-text("×")',

            # Generic modals and popups
            '[class*="modal"] button:has-text("×")',
            '[class*="modal"] .close',
            '[class*="popup"] button:has-text("×")',
            '[class*="popup"] .close',
            '[class*="overlay"] button:has-text("×")',
            '[class*="overlay"] .close',

            # Promotional/Newsletter popups
            '[class*="newsletter"] button:has-text("×")',
            '[class*="newsletter"] button:has-text("No Thanks")',
            '[class*="offer"] button:has-text("×")',
            '[class*="promotion"] button:has-text("×")',

            # Generic close buttons
            'button[aria-label*="close" i]',
            'button[title*="close" i]',
            '.close-button', '.btn-close', '.modal-close'
        ]

        for selector in popup_close_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                for i in range(min(count, 5)):  # Max 5 popup closures
                    element = elements.nth(i)
                    if await element.is_visible(timeout=1500):
                        await element.click()
                        overlays_handled += 1
                        print(f"   ❌ CLOSED popup")
                        await asyncio.sleep(random.uniform(0.3, 0.8))
            except:
                continue

        # Phase 5: Nuclear JavaScript cleanup
        try:
            await page.evaluate("""
                // Comprehensive overlay removal
                const removeOverlays = () => {
                    // Remove by class/id patterns
                    const selectors = [
                        '[id*="engagement"]', '[class*="engagement"]',
                        '[id*="layer"]', '[class*="layer"]',
                        '[id*="cover"]', '[class*="cover"]',
                        '[id*="modal"]:not(form [id*="modal"])', '[class*="modal"]:not(form [class*="modal"])',
                        '[id*="popup"]', '[class*="popup"]',
                        '[id*="overlay"]', '[class*="overlay"]',
                        '[id*="chat"]:not(form [id*="chat"])', '[class*="chat"]:not(form [class*="chat"])',
                        '[class*="intercom"]', '[id*="intercom"]'
                    ];

                    selectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            // Don't remove form elements
                            if (!el.closest('form') && !el.querySelector('form')) {
                                el.style.display = 'none';
                                el.style.visibility = 'hidden';
                                el.style.pointerEvents = 'none';
                                el.style.zIndex = '-9999';
                                el.remove();
                            }
                        });
                    });

                    // Remove high z-index blocking elements
                    const allElements = document.querySelectorAll('*');
                    allElements.forEach(element => {
                        const styles = window.getComputedStyle(element);
                        const zIndex = parseInt(styles.zIndex);

                        if (zIndex > 1000 && styles.position === 'fixed') {
                            const rect = element.getBoundingClientRect();
                            // Remove if it covers significant screen area and isn't a form
                            if ((rect.width > window.innerWidth * 0.3 || rect.height > window.innerHeight * 0.3) &&
                                !element.closest('form') && !element.querySelector('form')) {
                                element.style.display = 'none';
                                element.remove();
                            }
                        }
                    });
                };

                removeOverlays();
                console.log('Nuclear overlay cleanup completed');
            """)
            print(f"   💥 Nuclear JavaScript cleanup completed")
        except:
            pass

        if overlays_handled > 0:
            print(f"   ✅ Handled {overlays_handled} overlays total")

        return overlays_handled

    async def advanced_form_detection(self, page):
        """Advanced form detection with comprehensive field mapping."""

        print("🔍 Advanced form detection...")

        await page.wait_for_load_state("networkidle")

        # Wait for any dynamic content
        await asyncio.sleep(random.uniform(2, 4))

        detected_fields = {}

        # Comprehensive field patterns
        field_patterns = {
            'first_name': [
                'input[name*="first" i]:visible:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[id*="first" i]:visible',
                'input[placeholder*="first" i]:visible',
                'input[aria-label*="first" i]:visible',
                'input[name="fname"]:visible',
                'input[name="firstname"]:visible'
            ],
            'last_name': [
                'input[name*="last" i]:visible:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[id*="last" i]:visible',
                'input[placeholder*="last" i]:visible',
                'input[aria-label*="last" i]:visible',
                'input[name="lname"]:visible',
                'input[name="lastname"]:visible'
            ],
            'email': [
                'input[type="email"]:visible:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="email" i]:visible',
                'input[id*="email" i]:visible',
                'input[placeholder*="email" i]:visible'
            ],
            'phone': [
                'input[type="tel"]:visible:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="phone" i]:visible',
                'input[id*="phone" i]:visible',
                'input[placeholder*="phone" i]:visible',
                'input[name*="tel" i]:visible'
            ],
            'zip': [
                'input[name*="zip" i]:visible:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[name*="postal" i]:visible',
                'input[id*="zip" i]:visible',
                'input[placeholder*="zip" i]:visible'
            ],
            'message': [
                'textarea:visible:not([style*="display: none"]):not([style*="visibility: hidden"]):not([name*="honeypot"])',
                'textarea[name*="message" i]:visible',
                'textarea[id*="message" i]:visible',
                'textarea[placeholder*="message" i]:visible',
                'textarea[name*="comment" i]:visible'
            ]
        }

        for field_type, selectors in field_patterns.items():
            for selector in selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)

                        # Advanced honeypot detection
                        if await self._is_sophisticated_honeypot(page, element):
                            print(f"   🍯 HONEYPOT detected for {field_type} - skipping")
                            continue

                        if (await element.is_visible() and
                            await element.is_enabled()):
                            detected_fields[field_type] = element
                            print(f"   ✅ Found {field_type}")
                            break

                    if field_type in detected_fields:
                        break

                except Exception as e:
                    continue

        # Find submit button with enhanced detection
        submit_button = await self._find_submit_button(page)

        return detected_fields, submit_button

    async def _is_sophisticated_honeypot(self, page, element):
        """Sophisticated honeypot detection."""

        try:
            # Get comprehensive element info
            element_info = await element.evaluate("""
                element => {
                    const computed = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    const attrs = {};
                    for (let attr of element.attributes) {
                        attrs[attr.name] = attr.value;
                    }

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
                        rect: {
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            left: rect.left
                        },
                        attributes: attrs,
                        tagName: element.tagName,
                        isVisible: rect.width > 0 && rect.height > 0,
                        tabIndex: element.tabIndex
                    };
                }
            """)

            # Check for hidden elements
            if (element_info['display'] == 'none' or
                element_info['visibility'] == 'hidden' or
                float(element_info['opacity']) < 0.1):
                return True

            # Check for zero/micro size
            if (element_info['rect']['width'] <= 1 or
                element_info['rect']['height'] <= 1):
                return True

            # Check for off-screen positioning
            if (element_info['rect']['left'] < -100 or
                element_info['rect']['top'] < -100):
                return True

            # Check for honeypot keywords
            honeypot_patterns = [
                'honeypot', 'trap', 'bot', 'spam', 'hidden', 'invisible',
                'email_confirm', 'website', 'url', 'leave_blank', 'do_not_fill'
            ]

            all_text = ' '.join([
                str(element_info['attributes'].get('name', '')),
                str(element_info['attributes'].get('id', '')),
                str(element_info['attributes'].get('class', '')),
                str(element_info['attributes'].get('placeholder', ''))
            ]).lower()

            if any(pattern in all_text for pattern in honeypot_patterns):
                return True

            # Check for suspicious tabindex
            if element_info.get('tabIndex', 0) < 0:
                return True

            return False

        except:
            # If we can't determine, assume it's suspicious
            return True

    async def _find_submit_button(self, page):
        """Find submit button with comprehensive detection."""

        submit_selectors = [
            'button[type="submit"]:visible',
            'input[type="submit"]:visible',
            'button:has-text("Submit"):visible',
            'button:has-text("Send"):visible',
            'button:has-text("Send Message"):visible',
            'button:has-text("Contact Us"):visible',
            'button:has-text("Get Quote"):visible',
            'button:has-text("Request Info"):visible',
            'input[value*="Submit" i]:visible',
            'input[value*="Send" i]:visible'
        ]

        for selector in submit_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()

                for i in range(count):
                    element = elements.nth(i)

                    if (await element.is_visible() and
                        await element.is_enabled() and
                        not await self._is_sophisticated_honeypot(page, element)):
                        print(f"   ✅ Found submit button")
                        return element

            except:
                continue

        print(f"   ⚠️ No submit button found")
        return None

    async def precision_form_filling(self, page, detected_fields):
        """Precision form filling with advanced human simulation."""

        print("📝 Precision form filling...")

        # Clear any remaining overlays
        await self.ultimate_overlay_management(page)

        filled_count = 0

        for field_type, element in detected_fields.items():
            if hasattr(self.contact_data, field_type):
                try:
                    print(f"   📝 Filling {field_type}...")

                    # Ensure field is accessible
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                    # Advanced interaction check
                    try:
                        await element.hover(timeout=3000)
                    except Exception as e:
                        print(f"   🔧 Field blocked, aggressive cleanup...")
                        await self.ultimate_overlay_management(page)
                        await asyncio.sleep(2)

                    # Human-like field interaction
                    await element.click()
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                    # Clear existing content
                    await element.fill('')
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                    # Get value to type
                    value = getattr(self.contact_data, field_type)

                    # Ultra-realistic typing with variations
                    for i, char in enumerate(value):
                        await page.keyboard.type(char)

                        # Realistic typing rhythm
                        if char == ' ':
                            await asyncio.sleep(random.uniform(0.1, 0.3))
                        elif char in '.,!?':
                            await asyncio.sleep(random.uniform(0.2, 0.4))
                        elif i > 0 and i % 10 == 0:  # Pause every 10 chars
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                        else:
                            await asyncio.sleep(random.uniform(0.05, 0.12))

                    # Occasional realistic "correction"
                    if random.random() < 0.1:  # 10% chance
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        await page.keyboard.press('Backspace')
                        await asyncio.sleep(random.uniform(0.2, 0.4))
                        await page.keyboard.type(value[-1])

                    filled_count += 1
                    print(f"   ✅ Filled {field_type}")

                    # Human thinking time between fields
                    thinking_time = random.uniform(2, 6)
                    await asyncio.sleep(thinking_time)

                except Exception as e:
                    print(f"   ⚠️ Could not fill {field_type}: {e}")

        # Handle consent checkboxes
        await self._handle_consent_checkboxes(page)

        return filled_count

    async def _handle_consent_checkboxes(self, page):
        """Handle consent checkboxes intelligently."""

        print("☑️ Processing consent checkboxes...")

        checkbox_selectors = [
            'input[type="checkbox"]:visible',
            'input[name*="agree" i]:visible',
            'input[name*="consent" i]:visible',
            'input[name*="terms" i]:visible'
        ]

        checkboxes_checked = 0

        for selector in checkbox_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()

                for i in range(count):
                    checkbox = elements.nth(i)

                    # Skip if honeypot
                    if await self._is_sophisticated_honeypot(page, checkbox):
                        continue

                    if (await checkbox.is_visible() and
                        await checkbox.is_enabled() and
                        not await checkbox.is_checked()):

                        # Get label text to understand what we're agreeing to
                        try:
                            label_text = await checkbox.evaluate("""
                                element => {
                                    const id = element.id;
                                    const label = id ? document.querySelector(`label[for="${id}"]`) : null;
                                    return label ? label.textContent : '';
                                }
                            """)
                        except:
                            label_text = ""

                        # Only check consent/terms, not marketing
                        consent_keywords = ['agree', 'consent', 'terms', 'privacy', 'policy']
                        marketing_keywords = ['newsletter', 'marketing', 'promotional', 'offers']

                        if (any(keyword in label_text.lower() for keyword in consent_keywords) and
                            not any(keyword in label_text.lower() for keyword in marketing_keywords)):

                            await checkbox.scroll_into_view_if_needed()
                            await asyncio.sleep(random.uniform(0.5, 1))
                            await checkbox.hover()
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                            await checkbox.click()

                            checkboxes_checked += 1
                            print(f"   ✅ Checked consent checkbox")
                            await asyncio.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                continue

        if checkboxes_checked > 0:
            print(f"   ✅ Checked {checkboxes_checked} consent checkboxes")

        return checkboxes_checked

    async def intelligent_submission(self, page, submit_button):
        """Intelligent form submission with advanced confirmation detection."""

        print("🚀 Intelligent form submission...")

        if not submit_button:
            print("   ❌ No submit button available")
            return False

        try:
            # Final overlay cleanup before submission
            await self.ultimate_overlay_management(page)

            # Record initial state
            initial_url = page.url
            initial_title = await page.title()
            print(f"   📋 Initial URL: {initial_url}")

            # Ensure submit button accessibility
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(1, 2))

            # Human-like pre-submission behavior
            print("   🤔 Pre-submission review...")

            # Scroll up to "review" the form
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(random.uniform(1, 3))

            # Scroll back to submit area
            await submit_button.scroll_into_view_if_needed()
            await asyncio.sleep(random.uniform(1, 2))

            # Final hover and hesitation
            await submit_button.hover()
            await asyncio.sleep(random.uniform(2, 4))

            # Submit with error handling
            try:
                await submit_button.click(timeout=5000)
                print("   ✅ Submit button clicked")
            except Exception as e:
                print(f"   🔧 Normal click failed, trying force click: {e}")
                await submit_button.click(force=True)
                print("   ✅ Submit button force-clicked")

            # Enhanced confirmation detection
            return await self._detect_submission_success(page, initial_url, initial_title)

        except Exception as e:
            print(f"   ❌ Submission failed: {e}")
            return False

    async def _detect_submission_success(self, page, initial_url, initial_title):
        """Enhanced submission success detection."""

        print("   ⏳ Detecting submission success...")

        # Multi-phase detection with increasing delays
        phases = [
            {"delay_range": (1, 3), "checks": 2, "name": "immediate"},
            {"delay_range": (2, 4), "checks": 3, "name": "short-term"},
            {"delay_range": (3, 5), "checks": 3, "name": "extended"}
        ]

        for phase_idx, phase in enumerate(phases):
            print(f"   🔍 {phase['name']} detection phase...")

            for check in range(phase['checks']):
                await asyncio.sleep(random.uniform(*phase['delay_range']))

                try:
                    current_url = page.url
                    current_title = await page.title()
                    page_content = await page.content()

                    # Check for URL changes indicating success
                    if current_url != initial_url:
                        print(f"   🔄 URL changed to: {current_url}")

                        success_url_indicators = [
                            'thank', 'success', 'confirm', 'complete',
                            'submitted', 'received', 'sent'
                        ]

                        if any(indicator in current_url.lower() for indicator in success_url_indicators):
                            print("   🎉 SUCCESS: Success URL detected!")
                            self.success_rate.append(True)
                            return True

                    # Check for title changes
                    if current_title != initial_title:
                        success_title_indicators = [
                            'thank', 'success', 'confirm', 'complete', 'submitted'
                        ]

                        if any(indicator in current_title.lower() for indicator in success_title_indicators):
                            print("   🎉 SUCCESS: Success title detected!")
                            self.success_rate.append(True)
                            return True

                    # Check page content for success messages
                    success_content_patterns = [
                        "thank you", "thanks for", "received", "submitted",
                        "confirmation", "success", "complete", "sent",
                        "message sent", "inquiry sent", "form submitted",
                        "we'll be in touch", "contact you soon",
                        "received your message", "we'll contact you",
                        "submitted successfully", "inquiry received"
                    ]

                    if any(pattern in page_content.lower() for pattern in success_content_patterns):
                        print("   🎉 SUCCESS: Confirmation message detected!")
                        self.success_rate.append(True)
                        return True

                    # Check for blocking/error indicators
                    block_indicators = [
                        "blocked", "cloudflare", "access denied", "forbidden",
                        "rate limit", "too many requests"
                    ]

                    if any(indicator in page_content.lower() for indicator in block_indicators):
                        print("   ❌ BLOCKED: Security system blocked submission")
                        self.recent_blocks.append(datetime.now())
                        self.success_rate.append(False)
                        return False

                    # Check for form validation errors
                    error_indicators = [
                        "error", "required", "invalid", "please enter",
                        "field is required", "must be", "cannot be empty"
                    ]

                    error_count = sum(1 for error in error_indicators if error in page_content.lower())
                    if error_count >= 2:  # Multiple error indicators suggest validation failure
                        print("   ⚠️ Form validation errors detected")
                        self.success_rate.append(False)
                        return False

                    print(f"   ⏳ Phase {phase_idx + 1}, check {check + 1}/{phase['checks']}...")

                except Exception as e:
                    print(f"   ⚠️ Detection check failed: {e}")
                    continue

        # Final assessment
        final_url = page.url
        final_content = await page.content()

        if final_url != initial_url:
            print("   ❓ URL changed but no clear success indicator")
            self.success_rate.append(None)
            return "uncertain"
        elif any(word in final_content.lower() for word in ["blocked", "cloudflare"]):
            print("   ❌ Final assessment: blocked")
            self.recent_blocks.append(datetime.now())
            self.success_rate.append(False)
            return False
        else:
            print("   ❓ No definitive result detected")
            self.success_rate.append(None)
            return "uncertain"

    async def process_dealership_ultimate(self, dealer_name, contact_url):
        """Process single dealership with ultimate automation."""

        print(f"\n🎯 ULTIMATE PROCESSING: {dealer_name}")
        print(f"🔗 URL: {contact_url}")
        print("=" * 70)

        # Smart delay calculation
        if self.last_submission_time:
            delay = self.calculate_smart_delay()
            print(f"⏰ Smart delay: {delay:.1f} seconds")
            await asyncio.sleep(delay)

        playwright = None
        browser = None

        try:
            # Create ultimate stealth browser
            playwright, browser, page = await self.create_advanced_stealth_browser()

            # Intelligent session warmup
            await self.intelligent_session_warmup(page)

            # Navigate with stealth
            final_url = await self.comprehensive_stealth_navigation(page, contact_url)

            # Ultimate overlay management
            await self.ultimate_overlay_management(page)

            # Advanced form detection
            detected_fields, submit_button = await self.advanced_form_detection(page)

            if not detected_fields:
                print("❌ No form fields detected")
                return False

            print(f"✅ Detected {len(detected_fields)} fields")

            # Precision form filling
            filled_count = await self.precision_form_filling(page, detected_fields)

            if filled_count == 0:
                print("❌ No fields were filled")
                return False

            print(f"✅ Successfully filled {filled_count} fields")

            # Intelligent submission
            result = await self.intelligent_submission(page, submit_button)

            # Update tracking
            self.submissions_count += 1
            self.last_submission_time = datetime.now()

            if result is True:
                print("🎉 ULTIMATE SUCCESS: Dealership contacted!")
                return True
            elif result == "uncertain":
                print("❓ UNCERTAIN: Check email for confirmation")
                return "uncertain"
            else:
                print("❌ SUBMISSION FAILED")
                return False

        except Exception as e:
            print(f"💥 Ultimate processing error: {e}")
            return False

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

            # Cleanup delay
            await asyncio.sleep(random.uniform(2, 5))


async def test_ultimate_automation():
    """Test the ultimate automation system."""

    print("🏆 ULTIMATE DEALERSHIP AUTOMATION TEST")
    print("🎯 Maximum stealth • Residential IP optimized • Human behavior simulation")
    print("=" * 80)

    automation = UltimateDealershipAutomation()

    # Test with Capital City CDJR
    result = await automation.process_dealership_ultimate(
        dealer_name="Capital City CDJR (Ultimate Test)",
        contact_url="https://www.capcitycdjr.com/contact-us/"
    )

    print("\n" + "=" * 80)
    print("🏆 ULTIMATE AUTOMATION RESULTS:")

    if result is True:
        print("🎉 ULTIMATE SUCCESS!")
        print("   ✅ Form submitted successfully with confirmation detected")
        print("   ✅ Ready for production deployment")
    elif result == "uncertain":
        print("❓ UNCERTAIN RESULT")
        print("   ⚠️ Form submitted but confirmation unclear")
        print("   📧 Check email: migueljmontoya@protonmail.com")
    else:
        print("❌ SUBMISSION BLOCKED")
        print("   🔧 May need additional refinement")

    # Display session statistics
    print(f"\n📊 SESSION STATISTICS:")
    print(f"   🎯 Submissions attempted: {automation.submissions_count}")
    print(f"   📈 Recent success rate: {len([s for s in automation.success_rate[-5:] if s is True])}/5")
    print(f"   🚫 Recent blocks: {len(automation.recent_blocks)}")

    return result


if __name__ == "__main__":
    asyncio.run(test_ultimate_automation())