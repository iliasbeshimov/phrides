#!/usr/bin/env python3
"""
Enhanced stealth browser configuration with redirect handling and SSL bypass.
Implements next-generation anti-detection measures with redirect-aware automation.
"""

import asyncio
import random
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from typing import Dict, List, Optional, Tuple
import urllib3

# Disable SSL warnings for certificate bypass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EnhancedStealthBrowserManager:
    """Enhanced stealth browser manager with redirect and SSL handling"""
    
    def __init__(self):
        self.user_agents = [
            # Recent Chrome user agents for various OS
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        
        self.screen_resolutions = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]
    
    async def create_enhanced_stealth_browser(self, playwright_instance) -> Browser:
        """Create a browser instance with enhanced anti-detection and redirect handling"""
        
        # Launch with enhanced stealth arguments including SSL bypass
        browser = await playwright_instance.chromium.launch(
            headless=True,  # Can be False for debugging
            args=[
                # Basic stealth
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                
                # Enhanced anti-detection
                '--disable-automation',
                '--disable-infobars',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Faster loading
                
                # SSL and certificate handling
                '--ignore-ssl-errors',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--ignore-certificate-errors-spki-list-log',
                '--ignore-ssl-errors-list',
                '--allow-running-insecure-content',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--ssl-version-fallback-min=tls1',
                '--disable-ipc-flooding-protection',
                
                # Memory and performance
                '--memory-pressure-off',
                '--disable-renderer-backgrounding',
                '--disable-backgroundtimer-throttling',
                '--disable-background-networking',
                
                # Enhanced fingerprinting resistance
                '--disable-webgl',
                '--disable-accelerated-2d-canvas',
                '--disable-accelerated-jpeg-decoding',
                '--disable-accelerated-mjpeg-decode',
                '--disable-app-list-dismiss-on-blur',
                '--disable-accelerated-video-decode',
                '--disable-gpu',
                '--disable-gpu-sandbox',
                
                # Redirect and navigation handling
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
            ]
        )
        
        return browser
    
    async def create_enhanced_stealth_context(self, browser: Browser) -> BrowserContext:
        """Create a browser context with enhanced fingerprint and redirect handling"""
        
        # Random user agent and screen resolution
        user_agent = random.choice(self.user_agents)
        resolution = random.choice(self.screen_resolutions)
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=resolution,
            
            # Geolocation (random US location)
            geolocation={"latitude": 39.8283, "longitude": -98.5795},
            permissions=["geolocation"],
            
            # Language and locale
            locale="en-US",
            timezone_id="America/New_York",
            
            # Enhanced headers for redirect handling
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Connection": "keep-alive",
                "Accept-Insecure-Certs": "true",
            },
            
            # SSL and certificate bypass
            ignore_https_errors=True,
            accept_downloads=False,
        )
        
        return context
    
    async def create_enhanced_stealth_page(self, context: BrowserContext) -> Page:
        """Create a page with enhanced anti-detection and redirect tracking"""
        
        page = await context.new_page()
        
        # Enhanced scripts to hide automation signatures and handle redirects
        await page.add_init_script("""
            // Enhanced webdriver hiding
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Enhanced plugins mock
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {
                            type: "application/x-google-chrome-pdf",
                            suffixes: "pdf",
                            description: "Portable Document Format",
                        },
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {
                            type: "application/x-shockwave-flash",
                            suffixes: "swf",
                            description: "Shockwave Flash",
                        },
                        description: "Shockwave Flash 32.0 r0",
                        filename: "pepflashplayer.dll",
                        length: 1,
                        name: "Shockwave Flash"
                    }
                ],
            });
            
            // Enhanced languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es'],
            });
            
            // More comprehensive automation hiding
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Function;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_String;
            
            // Enhanced Chrome mock
            window.chrome = {
                runtime: {
                    onConnect: undefined,
                    onMessage: undefined,
                },
                loadTimes: function () {
                    return {
                        commitLoadTime: Date.now() / 1000 - Math.random(),
                        connectionInfo: 'http/1.1',
                        finishDocumentLoadTime: Date.now() / 1000 - Math.random(),
                        finishLoadTime: Date.now() / 1000 - Math.random(),
                        firstPaintAfterLoadTime: 0,
                        firstPaintTime: Date.now() / 1000 - Math.random(),
                        navigationType: 'Other',
                        npnNegotiatedProtocol: 'unknown',
                        requestTime: Date.now() / 1000 - Math.random(),
                        startLoadTime: Date.now() / 1000 - Math.random(),
                        wasAlternateProtocolAvailable: false,
                        wasFetchedViaSpdy: false,
                        wasNpnNegotiated: false
                    };
                },
                csi: function () {
                    return {
                        pageT: Date.now(),
                        startE: Date.now(),
                        tran: 15
                    };
                },
                app: {
                    isInstalled: false,
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    }
                }
            };
            
            // Enhanced permissions mock
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Enhanced connection mock
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    downlink: 10,
                    effectiveType: '4g',
                    rtt: 50,
                    saveData: false,
                })
            });
            
            // Mock battery API
            Object.defineProperty(navigator, 'getBattery', {
                get: () => () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1,
                })
            });
        """)
        
        # Set random viewport size
        resolution = random.choice(self.screen_resolutions)
        await page.set_viewport_size(resolution)
        
        return page
    
    async def navigate_with_redirect_handling(self, page: Page, url: str, max_redirects: int = 5) -> Tuple[bool, str, List[str]]:
        """Navigate to a URL with comprehensive redirect tracking and handling"""
        
        redirect_chain = []
        current_url = url
        
        for attempt in range(max_redirects + 1):
            try:
                print(f"      🔄 Navigation attempt {attempt + 1}: {current_url}")
                
                # Navigate with extended timeout for redirect handling
                response = await page.goto(current_url, 
                                         wait_until='domcontentloaded', 
                                         timeout=60000)
                
                # Wait for potential JavaScript redirects
                await self.human_like_delay(3000, 5000)
                
                final_url = page.url
                redirect_chain.append(final_url)
                
                print(f"         ✅ Landed on: {final_url}")
                
                # Check if we were redirected
                if final_url != current_url:
                    print(f"         🔄 Redirect detected: {current_url} → {final_url}")
                    
                    # If this is a different domain, continue with the redirected URL
                    if attempt < max_redirects:
                        current_url = final_url
                        continue
                
                # Successfully reached final destination
                return True, final_url, redirect_chain
                
            except Exception as e:
                error_msg = str(e)
                print(f"         ❌ Navigation failed: {error_msg[:50]}...")
                
                # If SSL error, try with HTTP fallback
                if "SSL" in error_msg or "certificate" in error_msg.lower():
                    if current_url.startswith("https://"):
                        http_url = current_url.replace("https://", "http://")
                        print(f"         🔄 Trying HTTP fallback: {http_url}")
                        try:
                            await page.goto(http_url, wait_until='domcontentloaded', timeout=45000)
                            await self.human_like_delay(2000, 3000)
                            final_url = page.url
                            redirect_chain.append(final_url)
                            return True, final_url, redirect_chain
                        except Exception as e2:
                            print(f"         ❌ HTTP fallback failed: {str(e2)[:50]}...")
                
                # If DNS error, this is likely a genuine failure
                if "ERR_NAME_NOT_RESOLVED" in error_msg:
                    return False, current_url, redirect_chain
                
                # For other errors, continue to next attempt if available
                if attempt < max_redirects:
                    await self.human_like_delay(2000, 3000)
                    continue
                else:
                    return False, current_url, redirect_chain
        
        return False, current_url, redirect_chain
    
    async def human_like_delay(self, min_ms: int = 1000, max_ms: int = 3000):
        """Add human-like delays between actions"""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)
    
    async def enhanced_human_like_typing(self, page: Page, selector: str, text: str):
        """Type text with enhanced human-like delays and error correction"""
        element = await page.locator(selector).first
        
        # Click element with random offset
        await element.click()
        await self.human_like_delay(200, 500)
        
        # Clear existing content
        await element.fill("")
        await self.human_like_delay(100, 300)
        
        # Type with realistic human patterns
        for i, char in enumerate(text):
            await element.type(char)
            
            # Random typing delays with occasional longer pauses
            if i > 0 and i % 5 == 0:  # Longer pause every 5 characters
                await asyncio.sleep(random.uniform(0.2, 0.4))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Occasional typo and correction (5% chance)
            if random.random() < 0.05 and i < len(text) - 1:
                wrong_char = chr(ord(char) + random.randint(-2, 2))
                await element.type(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.1, 0.2))
    
    async def enhanced_random_mouse_movement(self, page: Page):
        """Simulate enhanced random mouse movements with realistic patterns"""
        # Get page dimensions
        viewport = page.viewport_size
        max_x = viewport['width'] if viewport else 1920
        max_y = viewport['height'] if viewport else 1080
        
        # Create a realistic mouse path
        movements = random.randint(3, 8)
        current_x, current_y = random.randint(100, max_x//2), random.randint(100, max_y//2)
        
        for _ in range(movements):
            # Calculate next position with some smoothness
            next_x = max(50, min(max_x - 50, current_x + random.randint(-200, 200)))
            next_y = max(50, min(max_y - 50, current_y + random.randint(-150, 150)))
            
            # Move in small steps for more realistic movement
            steps = random.randint(3, 8)
            for step in range(steps):
                intermediate_x = current_x + (next_x - current_x) * (step + 1) / steps
                intermediate_y = current_y + (next_y - current_y) * (step + 1) / steps
                
                await page.mouse.move(intermediate_x, intermediate_y)
                await asyncio.sleep(random.uniform(0.02, 0.05))
            
            current_x, current_y = next_x, next_y
            
            # Occasional click on harmless area
            if random.random() < 0.3:
                await page.mouse.click(current_x, current_y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            await asyncio.sleep(random.uniform(0.1, 0.4))

# Enhanced convenience function for easy integration
async def create_enhanced_stealth_session():
    """Create a complete enhanced stealth browser session with redirect handling"""
    manager = EnhancedStealthBrowserManager()
    playwright_instance = await async_playwright().start()
    browser = await manager.create_enhanced_stealth_browser(playwright_instance)
    context = await manager.create_enhanced_stealth_context(browser)
    page = await manager.create_enhanced_stealth_page(context)
    
    return playwright_instance, browser, context, page, manager

# Test function to verify enhanced stealth measures
async def test_enhanced_stealth_with_redirects():
    """Test enhanced stealth measures including redirect handling"""
    playwright_instance, browser, context, page, manager = await create_enhanced_stealth_session()
    
    try:
        print("🕵️ Testing enhanced stealth measures with redirect handling...")
        
        # Test redirect handling with known redirect site
        test_url = "https://www.lhmdodgeram.com"
        print(f"🔄 Testing redirect handling: {test_url}")
        
        success, final_url, redirect_chain = await manager.navigate_with_redirect_handling(page, test_url)
        
        if success:
            print(f"✅ Successfully handled redirects!")
            print(f"   Final URL: {final_url}")
            print(f"   Redirect chain: {' → '.join(redirect_chain)}")
            
            # Test form detection on redirected site
            forms = await page.locator('form').all()
            print(f"   Forms found: {len(forms)}")
            
        else:
            print(f"❌ Redirect handling failed")
        
    finally:
        await browser.close()
        await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(test_enhanced_stealth_with_redirects())