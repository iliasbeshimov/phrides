"""
Creative and extensive contact page discovery strategies for maximum success rate.
Speed is not a concern - comprehensive discovery is the goal.
"""

import asyncio
import re
import json
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from playwright.async_api import Page, Locator
from dataclasses import dataclass

from ...utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ContactCandidate:
    """Enhanced contact candidate with rich metadata"""
    url: str
    text: str
    confidence: float
    source: str
    field_count: int = 0
    discovery_method: str = ""
    metadata: Dict = None


class CreativeContactHunter:
    """Ultra-comprehensive contact discovery using creative strategies"""
    
    def __init__(self):
        self.logger = logger
        self.discovered_urls = set()
        self.contact_indicators = []
        
        # Comprehensive keyword patterns
        self.contact_patterns = {
            'primary': [
                'contact', 'contact us', 'contact-us', 'contactus', 'reach us', 'get in touch'
            ],
            'inquiry': [
                'inquire', 'inquiry', 'ask', 'question', 'help', 'support'
            ],
            'quote': [
                'quote', 'get quote', 'request quote', 'price', 'estimate', 'get price'
            ],
            'service': [
                'service', 'schedule service', 'book service', 'appointment', 'schedule'
            ],
            'sales': [
                'sales', 'buy', 'purchase', 'test drive', 'financing'
            ],
            'location': [
                'location', 'directions', 'find us', 'visit us', 'hours', 'about'
            ],
            'communication': [
                'email', 'call', 'phone', 'message', 'chat', 'talk'
            ]
        }
        
        # Prioritized URL patterns based on previous successful discoveries
        self.proven_successful_patterns = [
            # HIGH-SUCCESS patterns found in previous tests (test these FIRST)
            '/contact.htm',           # Found in: napletonellwoodcity, oliviachryslercenter, stcharlescdj, cdjramsterdam
            '/contactus.aspx',        # Found in: monkenchrysler, cunninghamchryslerofedinboro, brookfieldchrysler
            '/contact-us/',           # Found in: spiritchryslerjeepdodge, wallyarmour, vinelandcdjr
            '/contact',               # Found in: jayhodgedodge, brandondcjr analysis
            '/contact-us',            # Alternative form without trailing slash
            '/contactus',             # Alternative form without extension
            '/serviceappmt.aspx',     # Found in: criswelljeepofwoodstock logs
        ]
        
        # Standard URL patterns for systematic testing (test after proven patterns)
        self.standard_url_patterns = [
            # Standard contact patterns
            '/contact/', '/contact.html', '/contact.php', '/contact.aspx',
            '/contact-us.html', '/contact-us.htm', '/contactus/', '/contactus.html', '/contactus.htm',
            
            # Quote/inquiry patterns
            '/quote', '/quote/', '/get-quote', '/get-quote/', '/request-quote',
            '/inquiry', '/inquire', '/ask', '/question',
            '/get-started', '/get_started',
            
            # Service patterns
            '/service', '/service/', '/schedule', '/schedule/', '/appointment',
            '/book-service', '/service-appointment', '/schedule-service',
            
            # About/info patterns
            '/about', '/about/', '/about-us', '/about-us/', '/info', '/information',
            '/directions', '/location', '/hours', '/visit',
            
            # Sales patterns
            '/sales', '/buy', '/purchase', '/financing', '/finance',
            
            # Alternative patterns discovered
            '/form', '/forms', '/feedback', '/support', '/help',
            '/reach-us', '/get-in-touch', '/connect',
            
            # Extension variations
            '/contact.php', '/contact.jsp', '/contact.cfm',
            '/contactus.php', '/contactus.jsp', '/contactus.cfm',
            '/contact-us.php', '/contact-us.jsp', '/contact-us.cfm'
        ]
        
        # Combined prioritized patterns list (proven patterns tested FIRST)
        self.url_patterns = self.proven_successful_patterns + self.standard_url_patterns
        
        # Creative discovery methods
        self.discovery_methods = [
            'navigation_parsing',
            'footer_mining',
            'sitemap_analysis',
            'robots_txt_analysis',
            'image_alt_text_analysis',
            'javascript_link_extraction',
            'meta_tag_analysis',
            'form_field_proximity_analysis',
            'url_pattern_brute_force',
            'text_content_pattern_matching',
            'iframe_deep_scan',
            'popup_trigger_analysis'
        ]

    async def comprehensive_contact_discovery(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Ultra-comprehensive contact discovery using all creative strategies"""
        
        self.logger.info("Starting comprehensive creative contact discovery", {
            "operation": "creative_discovery_start",
            "base_url": base_url,
            "methods": len(self.discovery_methods)
        })
        
        self.discovered_urls.clear()
        all_candidates = []
        
        try:
            # Navigate to homepage with extended timeout
            await page.goto(base_url, wait_until='networkidle', timeout=15000)
            await asyncio.sleep(3)  # Let everything load
            
            # Strategy 1: Enhanced Navigation Analysis
            nav_candidates = await self._strategy_navigation_deep_mining(page, base_url)
            all_candidates.extend(nav_candidates)
            
            # Strategy 2: Sitemap Discovery
            sitemap_candidates = await self._strategy_sitemap_analysis(page, base_url)
            all_candidates.extend(sitemap_candidates)
            
            # Strategy 3: Robots.txt Analysis
            robots_candidates = await self._strategy_robots_txt_analysis(page, base_url)
            all_candidates.extend(robots_candidates)
            
            # Strategy 4: JavaScript Link Extraction
            js_candidates = await self._strategy_javascript_mining(page, base_url)
            all_candidates.extend(js_candidates)
            
            # Strategy 5: Content Pattern Analysis
            content_candidates = await self._strategy_content_pattern_analysis(page, base_url)
            all_candidates.extend(content_candidates)
            
            # Strategy 6: Form Proximity Analysis
            proximity_candidates = await self._strategy_form_proximity_analysis(page, base_url)
            all_candidates.extend(proximity_candidates)
            
            # Strategy 7: Meta Tag Mining
            meta_candidates = await self._strategy_meta_tag_analysis(page, base_url)
            all_candidates.extend(meta_candidates)
            
            # Strategy 8: Iframe Deep Scan
            iframe_candidates = await self._strategy_iframe_deep_scan(page, base_url)
            all_candidates.extend(iframe_candidates)
            
            # Strategy 9: Systematic URL Pattern Testing
            pattern_candidates = await self._strategy_systematic_url_testing(page, base_url)
            all_candidates.extend(pattern_candidates)
            
            # Strategy 10: Image Alt Text Analysis
            image_candidates = await self._strategy_image_alt_analysis(page, base_url)
            all_candidates.extend(image_candidates)
            
            # Strategy 11: Popup/Modal Trigger Analysis
            popup_candidates = await self._strategy_popup_analysis(page, base_url)
            all_candidates.extend(popup_candidates)
            
            # Strategy 12: CSS Class/ID Mining
            css_candidates = await self._strategy_css_class_mining(page, base_url)
            all_candidates.extend(css_candidates)
            
            # Comprehensive deduplication and ranking
            final_candidates = self._comprehensive_deduplication_and_ranking(all_candidates)
            
            self.logger.info("Creative contact discovery completed", {
                "operation": "creative_discovery_complete",
                "total_raw_candidates": len(all_candidates),
                "final_candidates": len(final_candidates),
                "discovery_methods_used": len(set(c.discovery_method for c in all_candidates))
            })
            
            return final_candidates
            
        except Exception as e:
            self.logger.error("Creative contact discovery failed", {
                "operation": "creative_discovery_error",
                "error": str(e)
            })
            return []

    async def _strategy_navigation_deep_mining(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Deep navigation analysis including hidden menus and dropdowns"""
        
        candidates = []
        
        # Comprehensive navigation selectors including hidden elements
        nav_selectors = [
            # Standard navigation
            'nav a', 'nav button', 'nav li a', '.navigation a', '.navbar a',
            '.menu a', '.main-menu a', '.primary-menu a', '.top-menu a',
            '.site-nav a', '.site-navigation a', '.nav-menu a',
            
            # Header navigation
            'header a', '.header a', '.site-header a', '.page-header a',
            '.masthead a', '.banner a',
            
            # Footer navigation
            'footer a', '.footer a', '.site-footer a', '.page-footer a',
            '.footer-nav a', '.footer-menu a', '.footer-links a',
            
            # Hidden/dropdown menus
            '.dropdown a', '.dropdown-menu a', '.submenu a', '.sub-menu a',
            '.mobile-menu a', '.mobile-nav a', '.hamburger-menu a',
            
            # Button elements that might be links
            'button[onclick*="location"]', 'button[data-href]', 'button[data-url]',
            
            # Role-based selectors
            '[role="navigation"] a', '[role="menubar"] a', '[role="menu"] a',
            
            # Generic link selectors with filtering
            'a[href^="/"]', 'a[href^="http"]'
        ]
        
        for selector in nav_selectors:
            try:
                # Trigger any dropdowns or hidden menus first
                await self._trigger_dropdown_menus(page)
                
                elements = page.locator(selector)
                count = await elements.count()
                
                for i in range(min(count, 100)):  # Increased limit for thorough search
                    element = elements.nth(i)
                    
                    try:
                        # Get both visible and hidden text
                        text = await element.text_content()
                        inner_text = await element.inner_text()
                        href = await element.get_attribute('href')
                        
                        # Try multiple text sources
                        display_text = text or inner_text or ""
                        if not display_text and href:
                            # Extract text from URL if no display text
                            display_text = self._extract_text_from_url(href)
                        
                        if href and display_text:
                            confidence = self._calculate_comprehensive_confidence(display_text, href)
                            if confidence > 0:
                                full_url = urljoin(base_url, href)
                                candidates.append(ContactCandidate(
                                    url=full_url,
                                    text=display_text.strip(),
                                    confidence=confidence,
                                    source='navigation_deep_mining',
                                    discovery_method='navigation_parsing',
                                    metadata={'selector': selector, 'element_index': i}
                                ))
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return candidates

    async def _trigger_dropdown_menus(self, page: Page):
        """Trigger dropdown menus to reveal hidden navigation"""
        
        dropdown_triggers = [
            '.dropdown-toggle', '.menu-toggle', '.nav-toggle',
            '.hamburger', '.mobile-menu-toggle', '[data-toggle="dropdown"]',
            '.has-dropdown', '.menu-item-has-children'
        ]
        
        for trigger in dropdown_triggers:
            try:
                elements = page.locator(trigger)
                count = await elements.count()
                for i in range(min(count, 5)):  # Trigger first few
                    await elements.nth(i).hover()
                    await asyncio.sleep(0.5)
                    await elements.nth(i).click()
                    await asyncio.sleep(0.5)
            except:
                continue

    async def _strategy_sitemap_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Analyze sitemap.xml for contact-related URLs"""
        
        candidates = []
        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemaps.xml',
            '/sitemap.txt'
        ]
        
        for sitemap_path in sitemap_urls:
            try:
                sitemap_url = urljoin(base_url, sitemap_path)
                await page.goto(sitemap_url, wait_until='domcontentloaded', timeout=10000)
                
                # Get sitemap content
                content = await page.content()
                
                # Extract URLs from XML sitemap
                url_pattern = r'<loc>(.*?)</loc>'
                urls = re.findall(url_pattern, content)
                
                for url in urls:
                    if self._url_looks_like_contact(url):
                        confidence = self._calculate_url_confidence(url)
                        candidates.append(ContactCandidate(
                            url=url,
                            text=f'Sitemap: {self._extract_text_from_url(url)}',
                            confidence=confidence,
                            source='sitemap_analysis',
                            discovery_method='sitemap_analysis',
                            metadata={'sitemap_source': sitemap_path}
                        ))
                
                break  # Found working sitemap
                
            except Exception:
                continue
        
        return candidates

    async def _strategy_robots_txt_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Analyze robots.txt for sitemap references and disallowed contact pages"""
        
        candidates = []
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            await page.goto(robots_url, wait_until='domcontentloaded', timeout=10000)
            
            content = await page.content()
            text_content = await page.text_content('body')
            
            # Look for sitemap references
            sitemap_pattern = r'Sitemap:\s*(.*)'
            sitemaps = re.findall(sitemap_pattern, text_content, re.IGNORECASE)
            
            for sitemap_url in sitemaps:
                # Recursively analyze found sitemaps
                sub_candidates = await self._analyze_sitemap_url(page, sitemap_url.strip())
                candidates.extend(sub_candidates)
            
            # Look for disallowed paths that might be contact pages
            disallow_pattern = r'Disallow:\s*(/[^\s]*)'
            disallowed_paths = re.findall(disallow_pattern, text_content)
            
            for path in disallowed_paths:
                if self._url_looks_like_contact(path):
                    full_url = urljoin(base_url, path)
                    confidence = self._calculate_url_confidence(path)
                    candidates.append(ContactCandidate(
                        url=full_url,
                        text=f'Robots.txt: {self._extract_text_from_url(path)}',
                        confidence=confidence * 0.8,  # Lower confidence for disallowed
                        source='robots_txt_analysis',
                        discovery_method='robots_txt_analysis',
                        metadata={'found_in': 'disallow_list'}
                    ))
            
        except Exception:
            pass
        
        return candidates

    async def _strategy_javascript_mining(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Extract contact URLs from JavaScript code and data attributes"""
        
        candidates = []
        
        try:
            # Extract URLs from JavaScript variables and functions
            js_code = await page.evaluate("""
                () => {
                    const urls = [];
                    const scripts = document.querySelectorAll('script');
                    
                    scripts.forEach(script => {
                        if (script.textContent) {
                            // Look for URL patterns in JavaScript
                            const urlRegex = /['"`]([^'"`]*\/[^'"`]*contact[^'"`]*?)['"`]/gi;
                            const matches = script.textContent.match(urlRegex);
                            if (matches) {
                                matches.forEach(match => {
                                    const cleanUrl = match.replace(/['"`]/g, '');
                                    urls.push(cleanUrl);
                                });
                            }
                        }
                    });
                    
                    // Check data attributes
                    const elementsWithData = document.querySelectorAll('[data-href], [data-url], [data-link]');
                    elementsWithData.forEach(el => {
                        const dataHref = el.getAttribute('data-href') || el.getAttribute('data-url') || el.getAttribute('data-link');
                        if (dataHref && dataHref.includes('contact')) {
                            urls.push(dataHref);
                        }
                    });
                    
                    return urls;
                }
            """)
            
            for url in js_code:
                if self._url_looks_like_contact(url):
                    full_url = urljoin(base_url, url)
                    confidence = self._calculate_url_confidence(url)
                    candidates.append(ContactCandidate(
                        url=full_url,
                        text=f'JavaScript: {self._extract_text_from_url(url)}',
                        confidence=confidence,
                        source='javascript_mining',
                        discovery_method='javascript_link_extraction',
                        metadata={'extraction_method': 'javascript_regex'}
                    ))
            
        except Exception:
            pass
        
        return candidates

    async def _strategy_content_pattern_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Analyze page content for contact-related text patterns and nearby links"""
        
        candidates = []
        
        try:
            # Get all text content
            page_text = await page.text_content('body')
            
            # Look for contact-related text patterns
            contact_text_patterns = [
                r'contact\s+us\s+(?:at|on|via)?\s*([^\s]+)',
                r'reach\s+us\s+(?:at|on|via)?\s*([^\s]+)',
                r'email\s+us\s+(?:at)?\s*([^\s]+)',
                r'call\s+us\s+(?:at)?\s*([^\s]+)',
                r'visit\s+our\s+([^\s]*contact[^\s]*)',
                r'for\s+more\s+information[^.]*?([^\s]*contact[^\s]*)'
            ]
            
            for pattern in contact_text_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    potential_url = match.group(1) if match.groups() else match.group(0)
                    if '/' in potential_url or '.' in potential_url:
                        full_url = urljoin(base_url, potential_url)
                        candidates.append(ContactCandidate(
                            url=full_url,
                            text=f'Content pattern: {match.group(0)[:50]}',
                            confidence=0.6,
                            source='content_pattern_analysis',
                            discovery_method='text_content_pattern_matching',
                            metadata={'pattern': pattern, 'context': match.group(0)}
                        ))
            
        except Exception:
            pass
        
        return candidates

    async def _strategy_form_proximity_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Find links near existing forms on the page"""
        
        candidates = []
        
        try:
            # Find all forms
            forms = page.locator('form')
            form_count = await forms.count()
            
            for i in range(form_count):
                form = forms.nth(i)
                
                # Look for links near this form
                nearby_links = await form.locator('xpath=.//*[self::a or self::button]').all()
                
                for link in nearby_links:
                    try:
                        text = await link.text_content()
                        href = await link.get_attribute('href')
                        
                        if href and text:
                            confidence = self._calculate_comprehensive_confidence(text, href)
                            if confidence > 0:
                                full_url = urljoin(base_url, href)
                                candidates.append(ContactCandidate(
                                    url=full_url,
                                    text=text.strip(),
                                    confidence=confidence * 1.2,  # Boost for being near forms
                                    source='form_proximity_analysis',
                                    discovery_method='form_field_proximity_analysis',
                                    metadata={'near_form': True, 'form_index': i}
                                ))
                    except Exception:
                        continue
            
        except Exception:
            pass
        
        return candidates

    async def _strategy_systematic_url_testing(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Systematically test all URL patterns for working contact pages"""
        
        candidates = []
        base_domain = base_url.rstrip('/')
        
        self.logger.info("Starting systematic URL pattern testing", {
            "patterns_to_test": len(self.url_patterns)
        })
        
        for i, pattern in enumerate(self.url_patterns):
            test_url = base_domain + pattern
            
            try:
                # Test if URL exists and has forms
                await page.goto(test_url, wait_until='domcontentloaded', timeout=8000)
                
                # Quick form detection
                form_count = await self._comprehensive_form_detection(page)
                
                if form_count >= 1:  # Even 1 field could be useful
                    confidence = self._calculate_url_confidence(pattern)
                    candidates.append(ContactCandidate(
                        url=test_url,
                        text=f'Pattern test: {pattern}',
                        confidence=confidence,
                        source='systematic_url_testing',
                        discovery_method='url_pattern_brute_force',
                        field_count=form_count,
                        metadata={'pattern': pattern, 'test_order': i}
                    ))
                    
                    self.logger.info(f"Pattern test success: {test_url} - {form_count} fields")
                
            except Exception:
                continue
        
        return candidates

    async def _comprehensive_form_detection(self, page: Page) -> int:
        """Comprehensive form field detection"""
        
        form_selectors = [
            # Email inputs
            'input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]',
            'input[placeholder*="email" i]', 'input[class*="email" i]',
            
            # Text areas
            'textarea', 'textarea[name*="message" i]', 'textarea[name*="comment" i]',
            'textarea[placeholder*="message" i]', 'textarea[placeholder*="comment" i]',
            
            # Phone inputs
            'input[type="tel"]', 'input[name*="phone" i]', 'input[id*="phone" i]',
            'input[placeholder*="phone" i]', 'input[name*="mobile" i]',
            
            # Name inputs
            'input[name*="name" i]', 'input[id*="name" i]', 'input[placeholder*="name" i]',
            'input[name*="first" i]', 'input[name*="last" i]',
            
            # Generic text inputs in forms
            'form input[type="text"]', 'form input:not([type])',
            
            # Submit buttons (indicates form presence)
            'input[type="submit"]', 'button[type="submit"]',
            'input[value*="submit" i]', 'button[class*="submit" i]'
        ]
        
        total_fields = 0
        for selector in form_selectors:
            try:
                count = await page.locator(selector).count()
                total_fields += count
            except Exception:
                continue
        
        return total_fields

    def _url_looks_like_contact(self, url: str) -> bool:
        """Check if URL looks like it could be a contact page"""
        
        url_lower = url.lower()
        contact_indicators = [
            'contact', 'about', 'service', 'quote', 'inquiry', 'inquire',
            'schedule', 'appointment', 'sales', 'support', 'help',
            'location', 'directions', 'hours', 'reach', 'connect'
        ]
        
        return any(indicator in url_lower for indicator in contact_indicators)

    def _calculate_comprehensive_confidence(self, text: str, href: str) -> float:
        """Comprehensive confidence calculation considering multiple factors"""
        
        text_lower = text.lower().strip()
        href_lower = href.lower()
        
        # Primary contact terms (highest confidence)
        primary_terms = ['contact us', 'contact', 'get in touch', 'reach us']
        for term in primary_terms:
            if term in text_lower or term in href_lower:
                return 1.0
        
        # Quote/inquiry terms (high confidence)
        quote_terms = ['quote', 'get quote', 'request quote', 'estimate']
        for term in quote_terms:
            if term in text_lower or term in href_lower:
                return 0.9
        
        # Service terms (good confidence)
        service_terms = ['service', 'schedule', 'appointment', 'book']
        for term in service_terms:
            if term in text_lower or term in href_lower:
                return 0.8
        
        # About/info terms (medium confidence)
        info_terms = ['about', 'location', 'directions', 'hours', 'visit']
        for term in info_terms:
            if term in text_lower or term in href_lower:
                return 0.7
        
        # Communication terms (medium confidence)
        comm_terms = ['email', 'call', 'phone', 'message', 'chat']
        for term in comm_terms:
            if term in text_lower or term in href_lower:
                return 0.6
        
        return 0.0

    def _calculate_url_confidence(self, url: str) -> float:
        """Calculate confidence based on URL pattern"""
        
        url_lower = url.lower()
        
        if '/contact' in url_lower:
            return 0.95
        elif '/quote' in url_lower:
            return 0.85
        elif '/about' in url_lower or '/service' in url_lower:
            return 0.75
        elif any(term in url_lower for term in ['inquiry', 'schedule', 'appointment']):
            return 0.7
        else:
            return 0.5

    def _extract_text_from_url(self, url: str) -> str:
        """Extract meaningful text from URL"""
        
        # Remove domain and parameters
        path = urlparse(url).path
        
        # Split by slashes and clean
        parts = [part.replace('-', ' ').replace('_', ' ') for part in path.split('/') if part]
        
        return ' '.join(parts) if parts else url

    def _comprehensive_deduplication_and_ranking(self, candidates: List[ContactCandidate]) -> List[ContactCandidate]:
        """Comprehensive deduplication and intelligent ranking"""
        
        # Deduplicate by URL
        seen_urls = set()
        unique_candidates = []
        
        for candidate in candidates:
            url_normalized = candidate.url.rstrip('/').lower()
            if url_normalized not in seen_urls:
                seen_urls.add(url_normalized)
                unique_candidates.append(candidate)
        
        # Multi-factor sorting
        def sort_key(candidate):
            return (
                candidate.confidence,  # Primary: confidence
                candidate.field_count,  # Secondary: known form fields
                -len(candidate.url),  # Tertiary: shorter URLs preferred
                candidate.source == 'systematic_url_testing'  # Boost verified working URLs
            )
        
        unique_candidates.sort(key=sort_key, reverse=True)
        
        return unique_candidates[:25]  # Return top 25 candidates

    # Additional creative strategies
    async def _strategy_meta_tag_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Analyze meta tags for contact-related information"""
        
        candidates = []
        
        try:
            # Extract meta tag information
            meta_info = await page.evaluate("""
                () => {
                    const metas = [];
                    const metaTags = document.querySelectorAll('meta');
                    
                    metaTags.forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property') || meta.getAttribute('itemprop');
                        const content = meta.getAttribute('content');
                        
                        if (name && content) {
                            metas.push({name: name.toLowerCase(), content: content.toLowerCase()});
                        }
                    });
                    
                    return metas;
                }
            """)
            
            # Look for contact-related meta information
            contact_meta_patterns = [
                'contact', 'email', 'phone', 'address', 'location',
                'business:contact_data', 'og:phone_number', 'og:email'
            ]
            
            for meta in meta_info:
                for pattern in contact_meta_patterns:
                    if pattern in meta['name'] or pattern in meta['content']:
                        # Extract potential URLs from meta content
                        url_matches = re.findall(r'https?://[^\s]+', meta['content'])
                        for url in url_matches:
                            if self._url_looks_like_contact(url):
                                candidates.append(ContactCandidate(
                                    url=url,
                                    text=f'Meta tag: {meta["name"]}',
                                    confidence=0.7,
                                    source='meta_tag_analysis',
                                    discovery_method='meta_tag_analysis',
                                    metadata={'meta_name': meta['name'], 'meta_content': meta['content'][:100]}
                                ))
            
        except Exception:
            pass
        
        return candidates
    
    async def _strategy_iframe_deep_scan(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Deep scan of iframes for embedded contact forms"""
        
        candidates = []
        
        try:
            # Find all iframes
            iframes = page.locator('iframe')
            iframe_count = await iframes.count()
            
            for i in range(min(iframe_count, 10)):  # Check up to 10 iframes
                iframe = iframes.nth(i)
                
                try:
                    src = await iframe.get_attribute('src')
                    if src and self._url_looks_like_contact(src):
                        full_url = urljoin(base_url, src)
                        candidates.append(ContactCandidate(
                            url=full_url,
                            text=f'Iframe: {self._extract_text_from_url(src)}',
                            confidence=0.8,
                            source='iframe_deep_scan',
                            discovery_method='iframe_deep_scan',
                            metadata={'iframe_index': i, 'is_iframe': True}
                        ))
                    
                    # Try to access iframe content (same-origin only)
                    try:
                        iframe_content = await iframe.content_frame()
                        if iframe_content:
                            # Quick form check inside iframe
                            form_count = await iframe_content.locator('form, input[type="email"], textarea').count()
                            if form_count > 0:
                                iframe_url = await iframe_content.url()
                                candidates.append(ContactCandidate(
                                    url=iframe_url,
                                    text=f'Iframe content: forms detected',
                                    confidence=0.9,
                                    source='iframe_deep_scan',
                                    discovery_method='iframe_deep_scan',
                                    field_count=form_count,
                                    metadata={'iframe_index': i, 'is_iframe': True, 'has_forms': True}
                                ))
                    except:
                        pass  # Cross-origin iframe, can't access content
                        
                except Exception:
                    continue
            
        except Exception:
            pass
        
        return candidates
    
    async def _strategy_popup_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Trigger and analyze popups/modals for contact forms"""
        
        candidates = []
        
        try:
            # Look for popup/modal triggers
            popup_triggers = [
                'a[href="#contact"]', 'button[data-target*="contact"]',
                '.contact-popup', '.contact-modal', '[data-modal*="contact"]',
                'a[href*="popup"]', 'a[href*="modal"]',
                '[onclick*="popup"]', '[onclick*="modal"]'
            ]
            
            for trigger_selector in popup_triggers:
                try:
                    triggers = page.locator(trigger_selector)
                    trigger_count = await triggers.count()
                    
                    for i in range(min(trigger_count, 3)):  # Try first 3 triggers
                        trigger = triggers.nth(i)
                        
                        try:
                            # Click trigger to open popup/modal
                            await trigger.click()
                            await asyncio.sleep(2)  # Wait for popup to appear
                            
                            # Look for forms in newly appeared elements
                            modal_forms = await page.locator('.modal form, .popup form, [style*="display: block"] form').count()
                            
                            if modal_forms > 0:
                                # Get current URL (might change) or use base URL
                                current_url = page.url
                                trigger_text = await trigger.text_content()
                                
                                candidates.append(ContactCandidate(
                                    url=current_url,
                                    text=f'Popup trigger: {trigger_text or "Modal form"}',
                                    confidence=0.85,
                                    source='popup_analysis',
                                    discovery_method='popup_trigger_analysis',
                                    field_count=modal_forms,
                                    metadata={'trigger_selector': trigger_selector, 'is_popup': True}
                                ))
                            
                            # Close popup (try common methods)
                            try:
                                await page.locator('.modal .close, .popup .close, [data-dismiss="modal"]').first.click()
                            except:
                                await page.keyboard.press('Escape')
                            
                            await asyncio.sleep(1)
                            
                        except Exception:
                            continue
                        
                except Exception:
                    continue
            
        except Exception:
            pass
        
        return candidates
    
    async def _strategy_image_alt_analysis(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Analyze image alt text for contact-related information"""
        
        candidates = []
        
        try:
            # Get all images with alt text
            images = await page.evaluate("""
                () => {
                    const images = [];
                    const imgElements = document.querySelectorAll('img[alt]');
                    
                    imgElements.forEach(img => {
                        const alt = img.getAttribute('alt');
                        const src = img.getAttribute('src');
                        const parent = img.closest('a');
                        const parentHref = parent ? parent.getAttribute('href') : null;
                        
                        if (alt) {
                            images.push({
                                alt: alt.toLowerCase(),
                                src: src,
                                parentHref: parentHref
                            });
                        }
                    });
                    
                    return images;
                }
            """)
            
            # Look for contact-related alt text
            for img_info in images:
                alt_text = img_info['alt']
                
                # Check if alt text contains contact-related terms
                if any(term in alt_text for term in ['contact', 'email', 'phone', 'location', 'directions']):
                    if img_info['parentHref']:
                        full_url = urljoin(base_url, img_info['parentHref'])
                        confidence = self._calculate_comprehensive_confidence(alt_text, img_info['parentHref'])
                        
                        if confidence > 0:
                            candidates.append(ContactCandidate(
                                url=full_url,
                                text=f'Image alt: {alt_text}',
                                confidence=confidence * 0.8,  # Lower confidence for image-based
                                source='image_alt_analysis',
                                discovery_method='image_alt_text_analysis',
                                metadata={'alt_text': alt_text, 'image_src': img_info['src']}
                            ))
            
        except Exception:
            pass
        
        return candidates
    
    async def _strategy_css_class_mining(self, page: Page, base_url: str) -> List[ContactCandidate]:
        """Mine CSS classes and IDs for contact-related elements"""
        
        candidates = []
        
        try:
            # Find elements with contact-related CSS classes/IDs
            contact_css_patterns = [
                '[class*="contact"]', '[id*="contact"]',
                '[class*="quote"]', '[id*="quote"]',
                '[class*="inquiry"]', '[id*="inquiry"]',
                '[class*="service"]', '[id*="service"]',
                '[class*="appointment"]', '[id*="appointment"]'
            ]
            
            for pattern in contact_css_patterns:
                try:
                    elements = page.locator(pattern)
                    element_count = await elements.count()
                    
                    for i in range(min(element_count, 20)):
                        element = elements.nth(i)
                        
                        try:
                            # Check if element is a link
                            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                            
                            if tag_name == 'a':
                                href = await element.get_attribute('href')
                                text = await element.text_content()
                                
                                if href and text:
                                    full_url = urljoin(base_url, href)
                                    confidence = self._calculate_comprehensive_confidence(text, href)
                                    
                                    if confidence > 0:
                                        candidates.append(ContactCandidate(
                                            url=full_url,
                                            text=text.strip(),
                                            confidence=confidence,
                                            source='css_class_mining',
                                            discovery_method='css_class_mining',
                                            metadata={'css_pattern': pattern, 'element_index': i}
                                        ))
                            
                            # Check if element contains links
                            else:
                                links_in_element = element.locator('a')
                                link_count = await links_in_element.count()
                                
                                for j in range(min(link_count, 5)):
                                    link = links_in_element.nth(j)
                                    href = await link.get_attribute('href')
                                    text = await link.text_content()
                                    
                                    if href and text:
                                        full_url = urljoin(base_url, href)
                                        confidence = self._calculate_comprehensive_confidence(text, href)
                                        
                                        if confidence > 0:
                                            candidates.append(ContactCandidate(
                                                url=full_url,
                                                text=text.strip(),
                                                confidence=confidence,
                                                source='css_class_mining',
                                                discovery_method='css_class_mining',
                                                metadata={'css_pattern': pattern, 'parent_element': i, 'link_index': j}
                                            ))
                        
                        except Exception:
                            continue
                        
                except Exception:
                    continue
            
        except Exception:
            pass
        
        return candidates
    
    async def _analyze_sitemap_url(self, page: Page, sitemap_url: str) -> List[ContactCandidate]:
        """Analyze a specific sitemap URL"""
        
        candidates = []
        
        try:
            await page.goto(sitemap_url, wait_until='domcontentloaded', timeout=10000)
            content = await page.content()
            
            # Extract URLs from XML sitemap
            url_pattern = r'<loc>(.*?)</loc>'
            urls = re.findall(url_pattern, content)
            
            for url in urls:
                if self._url_looks_like_contact(url):
                    confidence = self._calculate_url_confidence(url)
                    candidates.append(ContactCandidate(
                        url=url,
                        text=f'Sitemap URL: {self._extract_text_from_url(url)}',
                        confidence=confidence,
                        source='sitemap_analysis',
                        discovery_method='sitemap_analysis',
                        metadata={'sitemap_source': sitemap_url}
                    ))
            
        except Exception:
            pass
        
        return candidates


class UltimateContactStrategy:
    """Ultimate contact discovery strategy combining all creative approaches"""
    
    def __init__(self):
        self.hunter = CreativeContactHunter()
        self.logger = logger
    
    async def find_and_verify_contact_pages(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Ultimate contact page discovery with maximum success rate"""
        
        self.logger.info("Starting ultimate contact strategy", {
            "operation": "ultimate_contact_start",
            "base_url": base_url
        })
        
        # Step 1: Comprehensive discovery
        candidates = await self.hunter.comprehensive_contact_discovery(page, base_url)
        
        if not candidates:
            self.logger.warning("No contact candidates found with ultimate strategy")
            return []
        
        # Step 2: Verification of top candidates
        verified_pages = []
        
        for candidate in candidates[:15]:  # Test top 15 candidates
            try:
                await page.goto(candidate.url, wait_until='domcontentloaded', timeout=10000)
                
                # Comprehensive form detection
                field_count = await self.hunter._comprehensive_form_detection(page)
                
                if field_count >= 1:  # Accept even single fields
                    verified_pages.append({
                        'url': candidate.url,
                        'text': candidate.text,
                        'confidence': candidate.confidence,
                        'source': candidate.source,
                        'discovery_method': candidate.discovery_method,
                        'field_count': field_count,
                        'verified': True,
                        'metadata': candidate.metadata
                    })
                    
                    self.logger.info(f"Ultimate strategy success", {
                        "url": candidate.url,
                        "method": candidate.discovery_method,
                        "field_count": field_count
                    })
            
            except Exception as e:
                self.logger.debug(f"Failed to verify {candidate.url}: {e}")
                continue
        
        self.logger.info("Ultimate contact strategy completed", {
            "operation": "ultimate_contact_complete",
            "candidates_found": len(candidates),
            "verified_pages": len(verified_pages),
            "success_rate": f"{len(verified_pages)/len(candidates)*100:.1f}%" if candidates else "0%"
        })
        
        return verified_pages