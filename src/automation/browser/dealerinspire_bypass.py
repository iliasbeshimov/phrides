"""
DealerInspire Cloudflare Bypass Strategy

DealerInspire sites use aggressive Cloudflare bot protection.
This module implements specialized techniques to bypass their detection.
"""

import asyncio
import random
from playwright.async_api import Page, BrowserContext


class DealerInspireBypass:
    """Specialized bypass for DealerInspire Cloudflare protection"""

    @staticmethod
    async def detect_dealerinspire(page: Page) -> bool:
        """Detect if page uses DealerInspire software"""
        try:
            content = await page.content()

            # Check for DealerInspire signatures
            dealerinspire_indicators = [
                'dealerinspire.com',
                'DealerInspire',
                'dealer-inspire',
                'di-cdn',  # DealerInspire CDN
            ]

            content_lower = content.lower()
            for indicator in dealerinspire_indicators:
                if indicator.lower() in content_lower:
                    print(f"      🔍 Detected DealerInspire software")
                    return True

            return False
        except Exception:
            return False

    @staticmethod
    async def wait_for_cloudflare_clearance(page: Page, max_wait: int = 30) -> bool:
        """Wait for Cloudflare challenge to complete"""
        print(f"      ⏳ Waiting for Cloudflare clearance...")

        try:
            # Wait for Cloudflare challenge page to disappear
            # Cloudflare typically shows: "Checking your browser..."
            start_time = asyncio.get_event_loop().time()

            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    print(f"      ⚠️  Cloudflare clearance timeout")
                    return False

                # Check if we're past the challenge
                try:
                    # Look for challenge indicators
                    challenge_present = await page.evaluate("""
                        () => {
                            const body = document.body.innerText.toLowerCase();
                            return body.includes('checking your browser') ||
                                   body.includes('cloudflare') ||
                                   body.includes('just a moment') ||
                                   document.querySelector('#challenge-running') !== null;
                        }
                    """)

                    if not challenge_present:
                        # Check if content loaded
                        forms = await page.locator('form').count()
                        if forms > 0:
                            print(f"      ✅ Cloudflare clearance obtained ({elapsed:.1f}s)")
                            return True

                    await asyncio.sleep(1)

                except Exception:
                    # If evaluate fails, page might be transitioning
                    await asyncio.sleep(1)
                    continue

        except Exception as e:
            print(f"      ❌ Error waiting for clearance: {e}")
            return False

    @staticmethod
    async def enhanced_navigation(page: Page, url: str) -> bool:
        """Navigate with DealerInspire-specific anti-detection"""
        try:
            print(f"      🚀 Using DealerInspire bypass navigation...")

            # Step 1: Navigate with realistic timing
            await page.goto(url, wait_until='domcontentloaded', timeout=45000)

            # Step 2: Wait for potential Cloudflare challenge
            await asyncio.sleep(random.uniform(2, 4))

            # Step 3: Simulate human-like behavior
            # Move mouse naturally
            viewport = page.viewport_size
            if viewport:
                for _ in range(3):
                    x = random.randint(100, viewport['width'] - 100)
                    y = random.randint(100, viewport['height'] - 100)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.3, 0.7))

            # Step 4: Scroll naturally (important for Cloudflare)
            await page.evaluate("""
                () => {
                    window.scrollTo({
                        top: Math.random() * 300,
                        behavior: 'smooth'
                    });
                }
            """)
            await asyncio.sleep(random.uniform(1, 2))

            # Step 5: Wait for Cloudflare clearance if needed
            is_di = await DealerInspireBypass.detect_dealerinspire(page)
            if is_di:
                await DealerInspireBypass.wait_for_cloudflare_clearance(page)

            # Step 6: Wait for forms to appear
            try:
                await page.wait_for_selector('form, .gform_wrapper', timeout=10000)
                print(f"      ✅ Forms detected after bypass")
            except:
                # Forms might be lazy-loaded
                await page.wait_for_load_state('networkidle', timeout=15000)

            # Step 7: Final delay for any lazy-loaded content
            await asyncio.sleep(random.uniform(2, 3))

            return True

        except Exception as e:
            print(f"      ❌ Enhanced navigation failed: {e}")
            return False

    @staticmethod
    async def inject_stealth_scripts(page: Page):
        """Inject additional anti-detection scripts for DealerInspire"""
        try:
            await page.add_init_script("""
                // Additional Cloudflare evasion

                // Override automation detection
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });

                // More realistic permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({state: 'default'});
                    }
                    return originalQuery(parameters);
                };

                // Hide Playwright/automation signals
                delete navigator.__proto__.webdriver;

                // Mock realistic browser behavior
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });

                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });

                // Mock realistic screen
                Object.defineProperty(screen, 'availWidth', {
                    get: () => window.innerWidth,
                });

                Object.defineProperty(screen, 'availHeight', {
                    get: () => window.innerHeight,
                });
            """)
            print(f"      🛡️  DealerInspire stealth scripts injected")
        except Exception as e:
            print(f"      ⚠️  Failed to inject stealth scripts: {e}")

    @staticmethod
    async def detect_and_handle_cloudflare_block(page: Page) -> bool:
        """Detect if we're being blocked by Cloudflare"""
        try:
            content = await page.content()
            title = await page.title()

            # Check for Cloudflare block indicators
            block_indicators = [
                'attention required',
                'cloudflare',
                'checking your browser',
                'just a moment',
                'enable javascript',
                'ray id',  # Cloudflare Ray ID in error pages
            ]

            content_lower = content.lower()
            title_lower = title.lower()

            for indicator in block_indicators:
                if indicator in content_lower or indicator in title_lower:
                    print(f"      🚫 Cloudflare block detected: '{indicator}'")
                    return True

            # Check for empty or minimal content
            text_content = await page.evaluate("() => document.body.innerText")
            if len(text_content.strip()) < 100:
                print(f"      🚫 Suspiciously empty page (possible block)")
                return True

            return False

        except Exception:
            return False


async def apply_dealerinspire_bypass(page: Page, url: str) -> bool:
    """
    Apply full DealerInspire bypass strategy

    Returns:
        True if bypass successful and page loaded
        False if blocked or failed
    """
    bypass = DealerInspireBypass()

    # Inject stealth scripts before navigation
    await bypass.inject_stealth_scripts(page)

    # Navigate with bypass techniques
    success = await bypass.enhanced_navigation(page, url)

    if not success:
        return False

    # Check if we're still being blocked
    is_blocked = await bypass.detect_and_handle_cloudflare_block(page)

    if is_blocked:
        print(f"      ⚠️  DealerInspire bypass unsuccessful - still blocked")

        # Try one more time with longer delay
        print(f"      🔄 Retrying with extended delay...")
        await asyncio.sleep(5)
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(random.uniform(3, 5))

        is_blocked = await bypass.detect_and_handle_cloudflare_block(page)
        if is_blocked:
            return False

    print(f"      ✅ DealerInspire bypass successful!")
    return True