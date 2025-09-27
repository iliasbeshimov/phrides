"""
Intelligent contact form finder that parses homepage navigation and links.
"""

import asyncio
import re
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, Locator

from ...utils.logging import get_logger

logger = get_logger(__name__)


class IntelligentContactFinder:
    """Finds contact forms by intelligently parsing homepage navigation"""
    
    def __init__(self):
        self.logger = logger
        
        # Contact-related keywords (prioritized)
        self.contact_keywords = [
            # Primary contact terms
            'contact', 'contact us', 'contact-us', 'contactus',
            # Quote/inquiry terms  
            'get quote', 'request quote', 'get a quote', 'quote',
            'request info', 'request information', 'inquire', 'inquiry',
            # Service terms
            'schedule service', 'book service', 'service appointment',
            # General action terms
            'get started', 'reach out', 'connect', 'talk to us',
            'email us', 'call us', 'message us', 'send message'
        ]
        
        # Navigation selectors to check
        self.nav_selectors = [
            'nav a', 'nav button',  # Main navigation
            '.nav a', '.navbar a', '.navigation a',  # Class-based nav
            '.menu a', '.main-menu a', '.primary-menu a',  # Menu classes
            'header a', '.header a',  # Header links
            '.footer a', 'footer a',  # Footer links (often have contact)
            '.contact-link', '.contact-btn',  # Direct contact classes
            'a[href*="contact"]',  # URLs containing contact
            'a[href*="quote"]',   # URLs containing quote
        ]
    
    async def find_contact_pages(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Find all potential contact pages from homepage navigation"""
        
        self.logger.info("Starting intelligent contact page discovery", {
            "operation": "contact_discovery_start",
            "url": page.url
        })
        
        contact_links = []
        
        try:
            # Wait for page to load
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Let dynamic content load
            
            # Strategy 1: Find navigation-based contact links
            nav_links = await self._find_navigation_contact_links(page, base_url)
            contact_links.extend(nav_links)
            
            # Strategy 2: Find contact forms directly on homepage
            homepage_forms = await self._check_homepage_forms(page)
            if homepage_forms:
                contact_links.append({
                    'url': page.url,
                    'text': 'Homepage Form',
                    'confidence': 0.9,
                    'source': 'homepage_form'
                })
            
            # Strategy 3: Find footer contact links
            footer_links = await self._find_footer_contact_links(page, base_url)
            contact_links.extend(footer_links)
            
            # Remove duplicates and sort by confidence
            unique_links = self._deduplicate_and_prioritize(contact_links)
            
            self.logger.info("Contact page discovery completed", {
                "operation": "contact_discovery_complete",
                "total_links": len(unique_links),
                "links": [link['url'] for link in unique_links[:5]]  # Log first 5
            })
            
            return unique_links
            
        except Exception as e:
            self.logger.error("Contact discovery failed", {
                "operation": "contact_discovery_error",
                "error": str(e)
            })
            return []
    
    async def _find_navigation_contact_links(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Find contact links in navigation menus"""
        
        nav_links = []
        
        for selector in self.nav_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                
                for i in range(min(count, 20)):  # Limit to first 20 to avoid performance issues
                    element = elements.nth(i)
                    
                    try:
                        # Get link text and href
                        text = await element.text_content()
                        href = await element.get_attribute('href')
                        
                        if not text or not href:
                            continue
                        
                        # Clean text
                        text = text.strip().lower()
                        if not text:
                            continue
                        
                        # Check if text matches contact keywords
                        confidence = self._calculate_text_confidence(text)
                        if confidence > 0:
                            # Resolve relative URLs
                            full_url = urljoin(base_url, href)
                            
                            nav_links.append({
                                'url': full_url,
                                'text': text,
                                'confidence': confidence,
                                'source': f'nav_{selector.replace(" ", "_")}'
                            })
                    
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return nav_links
    
    async def _find_footer_contact_links(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Find contact links in footer"""
        
        footer_links = []
        footer_selectors = ['.footer a', 'footer a', '#footer a']
        
        for selector in footer_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                
                for i in range(min(count, 10)):  # Check first 10 footer links
                    element = elements.nth(i)
                    
                    try:
                        text = await element.text_content()
                        href = await element.get_attribute('href')
                        
                        if text and href:
                            text = text.strip().lower()
                            confidence = self._calculate_text_confidence(text)
                            
                            if confidence > 0:
                                full_url = urljoin(base_url, href)
                                footer_links.append({
                                    'url': full_url,
                                    'text': text,
                                    'confidence': confidence * 0.8,  # Lower confidence for footer
                                    'source': 'footer'
                                })
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return footer_links
    
    async def _check_homepage_forms(self, page: Page) -> bool:
        """Quick check if homepage has contact forms"""
        
        form_selectors = [
            'form input[type="email"]',
            'form input[name*="email" i]',
            'form textarea',
            'input[type="email"] + input[type="text"]',  # Email + name pattern
        ]
        
        for selector in form_selectors:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    return True
            except Exception:
                continue
        
        return False
    
    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence score based on text matching contact keywords"""
        
        text = text.lower().strip()
        
        # Exact matches get highest confidence
        for keyword in self.contact_keywords:
            if text == keyword:
                return 1.0
        
        # Partial matches get medium confidence
        for keyword in self.contact_keywords:
            if keyword in text:
                # Higher confidence for shorter text (more specific)
                length_penalty = min(len(text) / 20, 0.3)
                return max(0.7 - length_penalty, 0.4)
        
        # Check for common contact patterns
        contact_patterns = [
            r'\bcontact\b', r'\bquote\b', r'\binquir[ye]\b',
            r'\bservice\b.*\bschedule\b', r'\bget\b.*\bstarted\b',
            r'\brequest\b.*\binfo\b'
        ]
        
        for pattern in contact_patterns:
            if re.search(pattern, text):
                return 0.5
        
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
        
        return unique_links[:10]  # Return top 10 candidates
    
    async def verify_contact_page(self, page: Page, url: str) -> Tuple[bool, int]:
        """Verify if a page actually contains contact forms"""
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=8000)
            await asyncio.sleep(1)  # Brief wait for forms to load
            
            # Quick form detection
            form_indicators = [
                'form input[type="email"]',
                'form input[name*="email" i]', 
                'form textarea',
                'input[type="email"]',
                'textarea[name*="message" i]',
                'input[name*="phone" i]'
            ]
            
            field_count = 0
            for selector in form_indicators:
                try:
                    count = await page.locator(selector).count()
                    field_count += count
                except Exception:
                    continue
            
            has_form = field_count >= 2  # Need at least 2 form fields
            
            self.logger.debug(f"Page verification: {url}", {
                "has_form": has_form,
                "field_count": field_count
            })
            
            return has_form, field_count
            
        except Exception as e:
            self.logger.debug(f"Page verification failed: {url}", {
                "error": str(e)
            })
            return False, 0


class SmartContactStrategy:
    """Combines intelligent contact finding with form detection"""
    
    def __init__(self):
        self.contact_finder = IntelligentContactFinder()
        self.logger = logger
    
    async def find_and_verify_contact_pages(self, page: Page, base_url: str) -> List[Dict[str, str]]:
        """Find contact pages and verify they have forms"""
        
        self.logger.info("Starting smart contact strategy", {
            "operation": "smart_contact_start",
            "base_url": base_url
        })
        
        # Step 1: Navigate to homepage and find contact links
        try:
            await page.goto(base_url, wait_until='domcontentloaded', timeout=10000)
        except Exception as e:
            self.logger.error(f"Failed to load homepage: {e}")
            return []
        
        # Step 2: Find all potential contact pages
        contact_candidates = await self.contact_finder.find_contact_pages(page, base_url)
        
        if not contact_candidates:
            self.logger.warning("No contact page candidates found")
            return []
        
        # Step 3: Verify each candidate page has forms
        verified_pages = []
        
        for candidate in contact_candidates[:5]:  # Test top 5 candidates
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
                    
                    self.logger.info(f"Verified contact page found", {
                        "url": url,
                        "text": candidate['text'],
                        "field_count": field_count
                    })
            
            except Exception as e:
                self.logger.debug(f"Failed to verify {url}: {e}")
                continue
        
        self.logger.info("Smart contact strategy completed", {
            "operation": "smart_contact_complete",
            "candidates_found": len(contact_candidates),
            "verified_pages": len(verified_pages)
        })
        
        return verified_pages