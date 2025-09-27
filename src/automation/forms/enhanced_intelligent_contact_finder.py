"""
Enhanced intelligent contact form finder with fallback strategies for 90%+ success rate.
"""

import asyncio
import re
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, Locator

from ...utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedIntelligentContactFinder:
    """Enhanced contact finder with multiple fallback strategies"""
    
    def __init__(self):
        self.logger = logger
        
        # Expanded contact keywords
        self.contact_keywords = [
            # Primary contact terms
            'contact', 'contact us', 'contact-us', 'contactus',
            # Quote/inquiry terms  
            'get quote', 'request quote', 'get a quote', 'quote', 'quotes',
            'request info', 'request information', 'inquire', 'inquiry',
            # Service terms
            'schedule service', 'book service', 'service appointment',
            'schedule appointment', 'appointment',
            # General action terms
            'get started', 'reach out', 'connect', 'talk to us',
            'email us', 'call us', 'message us', 'send message',
            # Additional terms found in analysis
            'about', 'about us', 'location', 'directions', 'hours',
            'service', 'parts', 'sales', 'financing'
        ]
        
        # Expanded navigation selectors
        self.nav_selectors = [
            # Standard navigation
            'nav a', 'nav button', 'nav li a',
            '.nav a', '.navbar a', '.navigation a',
            '.menu a', '.main-menu a', '.primary-menu a',
            '.top-menu a', '.site-nav a', '.site-navigation a',
            
            # Header/footer
            'header a', '.header a', '.site-header a',
            '.footer a', 'footer a', '.site-footer a',
            
            # Specific contact classes
            '.contact-link', '.contact-btn', '.contact-button',
            
            # Role-based selectors
            '[role="navigation"] a', '.navigation-menu a',
            
            # URL-based selectors
            'a[href*="contact"]', 'a[href*="quote"]',
            'a[href*="about"]', 'a[href*="service"]',
            
            # General link selectors as fallback
            'a[href^="/"]', 'a[href^="http"]'
        ]
        
        # Standard URL patterns to test as fallback
        self.fallback_url_patterns = [
            '/contact',
            '/contact-us',  
            '/contact-us/',
            '/contact.html',
            '/contact.htm',
            '/contactus',
            '/contactus/',
            '/contactus.html',
            '/contactus.htm',
            '/contactus.aspx',
            '/contact.aspx',
            '/contact-us.html',
            '/contact-us.htm',
            '/about',
            '/about-us',
            '/about/',
            '/service',
            '/service/',
            '/quote',
            '/get-quote',
            '/request-quote'
        ]
    
    async def find_contact_pages(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Enhanced contact page discovery with multiple strategies"""
        
        self.logger.info("Starting enhanced intelligent contact page discovery", {
            "operation": "enhanced_contact_discovery_start",
            "url": page.url
        })
        
        contact_links = []
        
        try:
            # Wait for page to load
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Let dynamic content load
            
            # Strategy 1: Enhanced navigation parsing
            nav_links = await self._find_enhanced_navigation_links(page, base_url)
            contact_links.extend(nav_links)
            
            # Strategy 2: Homepage forms detection (improved)
            homepage_forms = await self._check_enhanced_homepage_forms(page)
            if homepage_forms:
                contact_links.append({
                    'url': page.url,
                    'text': 'Homepage Form',
                    'confidence': 0.95,
                    'source': 'homepage_form',
                    'field_count': homepage_forms
                })
            
            # Strategy 3: Footer links (expanded)
            footer_links = await self._find_enhanced_footer_links(page, base_url)
            contact_links.extend(footer_links)
            
            # Strategy 4: FALLBACK - Test standard URL patterns if no links found
            if len(contact_links) == 0:
                self.logger.info("No navigation links found, using fallback URL patterns")
                fallback_links = await self._test_fallback_url_patterns(page, base_url)
                contact_links.extend(fallback_links)
            
            # Remove duplicates and sort by confidence
            unique_links = self._deduplicate_and_prioritize(contact_links)
            
            self.logger.info("Enhanced contact page discovery completed", {
                "operation": "enhanced_contact_discovery_complete",
                "total_links": len(unique_links),
                "strategies_used": list(set([link.get('source', 'unknown') for link in unique_links])),
                "top_links": [{'url': link['url'], 'confidence': link['confidence']} for link in unique_links[:3]]
            })
            
            return unique_links
            
        except Exception as e:
            self.logger.error("Enhanced contact discovery failed", {
                "operation": "enhanced_contact_discovery_error",
                "error": str(e)
            })
            return []
    
    async def _find_enhanced_navigation_links(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Enhanced navigation link finding with more selectors"""
        
        nav_links = []
        
        for selector in self.nav_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                
                # Increased limit for broader search
                for i in range(min(count, 50)):
                    element = elements.nth(i)
                    
                    try:
                        # Get link text and href
                        text = await element.text_content()
                        href = await element.get_attribute('href')
                        
                        if not text or not href:
                            continue
                        
                        # Clean text
                        text = text.strip().lower()
                        if not text or len(text) > 100:  # Skip very long text
                            continue
                        
                        # Enhanced confidence calculation
                        confidence = self._calculate_enhanced_confidence(text, href)
                        if confidence > 0:
                            # Resolve relative URLs
                            full_url = urljoin(base_url, href)
                            
                            nav_links.append({
                                'url': full_url,
                                'text': text,
                                'confidence': confidence,
                                'source': f'nav_{selector.replace(" ", "_").replace("[", "").replace("]", "")}'
                            })
                    
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return nav_links
    
    async def _find_enhanced_footer_links(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Enhanced footer link discovery"""
        
        footer_links = []
        footer_selectors = [
            '.footer a', 'footer a', '#footer a', '.site-footer a',
            '.footer-nav a', '.footer-menu a', '.footer-links a'
        ]
        
        for selector in footer_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                
                for i in range(min(count, 20)):  # Check more footer links
                    element = elements.nth(i)
                    
                    try:
                        text = await element.text_content()
                        href = await element.get_attribute('href')
                        
                        if text and href:
                            text = text.strip().lower()
                            confidence = self._calculate_enhanced_confidence(text, href)
                            
                            if confidence > 0:
                                full_url = urljoin(base_url, href)
                                footer_links.append({
                                    'url': full_url,
                                    'text': text,
                                    'confidence': confidence * 0.9,  # Slightly lower confidence for footer
                                    'source': 'footer'
                                })
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return footer_links
    
    async def _check_enhanced_homepage_forms(self, page: Page) -> int:
        """Enhanced homepage form detection"""
        
        form_selectors = [
            # Email inputs
            'form input[type="email"]',
            'input[type="email"]',
            'form input[name*="email" i]',
            'input[name*="email" i]',
            
            # Text areas (often message fields)
            'form textarea',
            'textarea',
            'textarea[name*="message" i]',
            'textarea[name*="comment" i]',
            
            # Phone inputs
            'form input[name*="phone" i]',
            'input[name*="phone" i]',
            'input[type="tel"]',
            
            # Name inputs
            'form input[name*="name" i]',
            'input[name*="name" i]',
            
            # Common contact form patterns
            'input[name*="first" i]',
            'input[name*="last" i]',
        ]
        
        total_fields = 0
        for selector in form_selectors:
            try:
                count = await page.locator(selector).count()
                total_fields += count
            except Exception:
                continue
        
        return total_fields if total_fields >= 2 else 0
    
    async def _test_fallback_url_patterns(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Test standard URL patterns when navigation parsing fails"""
        
        self.logger.info("Testing fallback URL patterns")
        fallback_links = []
        
        base_domain = base_url.rstrip('/')
        
        for pattern in self.fallback_url_patterns:
            test_url = base_domain + pattern
            
            try:
                # Quick navigation test
                await page.goto(test_url, wait_until='domcontentloaded', timeout=5000)
                
                # Quick form check
                form_count = await self._quick_form_check(page)
                
                if form_count >= 2:
                    fallback_links.append({
                        'url': test_url,
                        'text': f'Fallback: {pattern}',
                        'confidence': 0.8,  # Good confidence for working URLs
                        'source': 'fallback_pattern',
                        'field_count': form_count
                    })
                    
                    self.logger.info(f"Fallback success: {test_url} - {form_count} fields")
                
            except Exception:
                # URL doesn't exist or failed to load
                continue
        
        return fallback_links
    
    async def _quick_form_check(self, page: Page) -> int:
        """Quick form field count check"""
        
        form_indicators = [
            'form input[type="email"]',
            'input[type="email"]',
            'form input[name*="email" i]', 
            'form textarea',
            'textarea',
            'input[type="tel"]',
            'input[name*="phone" i]',
            'input[name*="name" i]'
        ]
        
        field_count = 0
        for selector in form_indicators:
            try:
                count = await page.locator(selector).count()
                field_count += count
            except Exception:
                continue
        
        return field_count
    
    def _calculate_enhanced_confidence(self, text: str, href: str) -> float:
        """Enhanced confidence calculation"""
        
        text = text.lower().strip()
        href = href.lower()
        
        # Exact matches get highest confidence
        high_priority_terms = ['contact', 'contact us', 'contact-us', 'contactus']
        for term in high_priority_terms:
            if text == term or term in href:
                return 1.0
        
        # Quote terms get high confidence
        quote_terms = ['quote', 'get quote', 'request quote']
        for term in quote_terms:
            if term in text or term in href:
                return 0.9
        
        # Service/appointment terms
        service_terms = ['service', 'appointment', 'schedule']
        for term in service_terms:
            if term in text or term in href:
                return 0.8
        
        # General contact-related terms
        for keyword in self.contact_keywords:
            if keyword in text or keyword in href:
                # Higher confidence for shorter, more specific text
                length_penalty = min(len(text) / 30, 0.2)
                return max(0.7 - length_penalty, 0.5)
        
        # URL-based matching
        contact_url_patterns = [
            r'/contact', r'/about', r'/service', r'/quote'
        ]
        
        for pattern in contact_url_patterns:
            if re.search(pattern, href):
                return 0.6
        
        return 0.0
    
    def _deduplicate_and_prioritize(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicates and sort by confidence"""
        
        # Deduplicate by URL
        seen_urls = set()
        unique_links = []
        
        for link in links:
            url = link['url'].rstrip('/')  # Remove trailing slash for comparison
            if url not in seen_urls:
                seen_urls.add(url)
                unique_links.append(link)
        
        # Sort by confidence (highest first)
        unique_links.sort(key=lambda x: x['confidence'], reverse=True)
        
        return unique_links[:15]  # Return top 15 candidates
    
    async def verify_contact_page(self, page: Page, url: str) -> Tuple[bool, int]:
        """Enhanced contact page verification"""
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=8000)
            await asyncio.sleep(1)  # Brief wait for forms to load
            
            # Enhanced form detection
            form_indicators = [
                'form input[type="email"]',
                'input[type="email"]',
                'form input[name*="email" i]', 
                'form textarea',
                'textarea[name*="message" i]',
                'input[name*="phone" i]',
                'input[type="tel"]',
                'input[name*="name" i]',
                'input[name*="first" i]',
                'input[name*="last" i]'
            ]
            
            field_count = 0
            for selector in form_indicators:
                try:
                    count = await page.locator(selector).count()
                    field_count += count
                except Exception:
                    continue
            
            has_form = field_count >= 2  # Need at least 2 form fields
            
            self.logger.debug(f"Enhanced page verification: {url}", {
                "has_form": has_form,
                "field_count": field_count
            })
            
            return has_form, field_count
            
        except Exception as e:
            self.logger.debug(f"Enhanced page verification failed: {url}", {
                "error": str(e)
            })
            return False, 0


class EnhancedSmartContactStrategy:
    """Enhanced smart contact strategy with 90%+ target success rate"""
    
    def __init__(self):
        self.contact_finder = EnhancedIntelligentContactFinder()
        self.logger = logger
    
    async def find_and_verify_contact_pages(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Enhanced contact page discovery and verification"""
        
        self.logger.info("Starting enhanced smart contact strategy", {
            "operation": "enhanced_smart_contact_start",
            "base_url": base_url
        })
        
        # Step 1: Navigate to homepage
        try:
            await page.goto(base_url, wait_until='domcontentloaded', timeout=10000)
        except Exception as e:
            self.logger.error(f"Failed to load homepage: {e}")
            return []
        
        # Step 2: Enhanced contact page discovery
        contact_candidates = await self.contact_finder.find_contact_pages(page, base_url)
        
        if not contact_candidates:
            self.logger.warning("No contact page candidates found")
            return []
        
        # Step 3: Verify each candidate (test more candidates)
        verified_pages = []
        
        for candidate in contact_candidates[:10]:  # Test top 10 candidates
            url = candidate['url']
            
            try:
                has_form, field_count = await self.contact_finder.verify_contact_page(page, url)
                
                if has_form:
                    verified_pages.append({
                        'url': url,
                        'text': candidate['text'],
                        'confidence': candidate['confidence'],
                        'source': candidate['source'],
                        'field_count': field_count,
                        'verified': True
                    })
                    
                    self.logger.info(f"Enhanced verified contact page found", {
                        "url": url,
                        "text": candidate['text'],
                        "field_count": field_count,
                        "source": candidate['source']
                    })
            
            except Exception as e:
                self.logger.debug(f"Failed to verify {url}: {e}")
                continue
        
        self.logger.info("Enhanced smart contact strategy completed", {
            "operation": "enhanced_smart_contact_complete",
            "candidates_found": len(contact_candidates),
            "verified_pages": len(verified_pages),
            "success_rate": f"{len(verified_pages)/len(contact_candidates)*100:.1f}%" if contact_candidates else "0%"
        })
        
        return verified_pages