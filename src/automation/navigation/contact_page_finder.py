"""
Intelligent contact page finder that detects contact URLs from homepage links.
Addresses the issue where sites use non-standard contact URLs like /contactus.aspx

Features:
- Checks cache first for previously discovered URLs
- Searches for contact links on homepage
- Validates form quality (multi-attempt if needed)
- Caches successful discoveries for future use
"""

import asyncio
from typing import Optional, List, Tuple, Dict
from playwright.async_api import Page
from ...utils.logging import get_logger
from ...services.contact_url_cache import ContactURLCache

logger = get_logger(__name__)


class ContactPageFinder:
    """Finds contact pages by analyzing homepage links"""

    def __init__(self, use_cache: bool = True):
        self.logger = logger
        self.use_cache = use_cache
        self.cache = ContactURLCache() if use_cache else None

    async def find_contact_url(self, page: Page, base_url: str, find_all: bool = False) -> Optional[str] | List[str]:
        """
        Find contact page URL by:
        1. Checking cache first (if enabled)
        2. Looking for contact links in navigation/header
        3. Trying common contact URL patterns

        Args:
            page: Playwright page object (should be on homepage or any page)
            base_url: Base website URL
            find_all: If True, return all found contact URLs (for multi-attempt)

        Returns:
            Contact page URL if found (or list if find_all=True), None otherwise
        """

        # Strategy 0: Check cache first
        if self.cache:
            cached_entry = self.cache.get_contact_url(base_url)
            if cached_entry and cached_entry.has_form:
                self.logger.info(f"Using cached contact URL: {cached_entry.contact_url}")
                return cached_entry.contact_url

        # Strategy 1: Find ALL contact links on current page
        contact_links = await self._find_all_contact_links_on_page(page, base_url)

        if contact_links and not find_all:
            # If not finding all, return first link immediately
            self.logger.info(f"Found {len(contact_links)} contact links on page")
            return contact_links[0]  # Return best match

        # Strategy 2: Try common contact URL patterns
        # ALWAYS try these patterns when find_all=True to get comprehensive list
        common_patterns = [
            "/contact.htm",         # Dealer.com pattern (very common)
            "/contactus.aspx",      # ASP.NET pattern (common for dealer sites)
            "/contact-us/",
            "/contact/",
            "/contactus.html",
            "/contact-us.aspx",
            "/contact.aspx",
            "/get-in-touch/",
            "/reach-us/",
        ]

        found_urls = []
        for pattern in common_patterns:
            url = f"{base_url.rstrip('/')}{pattern}"

            # Skip if already found via homepage links
            if contact_links and url in contact_links:
                found_urls.append(url)
                continue

            try:
                # Quick check if URL exists (without full load)
                response = await page.goto(url, wait_until="domcontentloaded", timeout=5000)
                if response and response.ok:
                    self.logger.info(f"Found contact page at: {url}")
                    found_urls.append(url)
                    if not find_all:
                        return url
            except:
                continue

        # Combine results: homepage links + pattern matches
        all_urls = []
        if contact_links:
            all_urls.extend(contact_links)
            self.logger.info(f"Found {len(contact_links)} contact links from homepage")

        # Add pattern matches that aren't duplicates
        for url in found_urls:
            if url not in all_urls:
                all_urls.append(url)

        if all_urls:
            self.logger.info(f"Total contact URLs found: {len(all_urls)}")

        if find_all:
            return all_urls if all_urls else None

        return all_urls[0] if all_urls else None

    async def _try_common_patterns_direct(self, base_url: str, page: Page, form_validator=None) -> List[str]:
        """
        Try common contact URL patterns directly (when homepage fails or no links found)

        Returns:
            List of contact URLs that have valid forms
        """
        common_patterns = [
            "/contactus.aspx",      # ASP.NET pattern (MOST common)
            "/contact-us/",
            "/contact/",
            "/contact.htm",         # Dealer.com pattern
            "/contactus.html",
            "/contact-us.aspx",
            "/contact.aspx",
            "/get-in-touch/",
            "/reach-us/",
        ]

        valid_urls = []

        for pattern in common_patterns:
            url = f"{base_url.rstrip('/')}{pattern}"

            try:
                self.logger.debug(f"Trying pattern: {url}")
                response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)

                if response and response.ok:
                    self.logger.info(f"Pattern matched: {url}")
                    await asyncio.sleep(1)

                    # Validate form if validator provided
                    if form_validator:
                        success, form_data = await form_validator(page)
                        if success:
                            self.logger.info(f"✅ Pattern {pattern} has valid form")
                            valid_urls.append(url)
                    else:
                        valid_urls.append(url)

            except Exception as e:
                self.logger.debug(f"Pattern {pattern} failed: {str(e)}")
                continue

        return valid_urls if valid_urls else None

    async def _find_all_contact_links_on_page(self, page: Page, base_url: str) -> List[str]:
        """
        Find ALL contact links on current page by analyzing navigation and links.

        Returns:
            List of contact URLs (prioritized), empty list if none found
        """

        try:
            # JavaScript to find contact links
            contact_links = await page.evaluate("""
                () => {
                    // Find all links
                    const links = Array.from(document.querySelectorAll('a[href]'));

                    // Contact keywords to search for
                    const contactKeywords = [
                        'contact', 'contactus', 'contact-us', 'get in touch',
                        'reach us', 'reach-us', 'contact us'
                    ];

                    const foundLinks = [];

                    for (const link of links) {
                        const href = link.getAttribute('href') || '';
                        const text = (link.textContent || '').toLowerCase().trim();
                        const title = (link.getAttribute('title') || '').toLowerCase();
                        const ariaLabel = (link.getAttribute('aria-label') || '').toLowerCase();

                        // Check if href, text, title, or aria-label contains contact keywords
                        const hrefLower = href.toLowerCase();
                        const hasContactKeyword = contactKeywords.some(keyword => {
                            return (
                                hrefLower.includes(keyword) ||
                                text.includes(keyword) ||
                                title.includes(keyword) ||
                                ariaLabel.includes(keyword)
                            );
                        });

                        if (hasContactKeyword) {
                            foundLinks.push({
                                href: href,
                                text: text,
                                isNavigation: link.closest('nav, header, .nav, .navigation, .menu') !== null
                            });
                        }
                    }

                    // Prioritize navigation links
                    foundLinks.sort((a, b) => {
                        if (a.isNavigation && !b.isNavigation) return -1;
                        if (!a.isNavigation && b.isNavigation) return 1;
                        return 0;
                    });

                    return foundLinks;
                }
            """)

            if not contact_links or len(contact_links) == 0:
                return []

            # Process ALL contact links and convert to absolute URLs
            result_urls = []
            for link in contact_links:
                href = link['href']

                # Convert relative URLs to absolute
                if href.startswith('/'):
                    url = f"{base_url.rstrip('/')}{href}"
                elif href.startswith('http'):
                    url = href
                elif not href.startswith('#'):
                    url = f"{base_url.rstrip('/')}/{href}"
                else:
                    continue  # Skip anchor links

                if url not in result_urls:
                    result_urls.append(url)

            return result_urls

        except Exception as e:
            self.logger.debug(f"Error finding contact links on page: {str(e)}")
            return []

    async def navigate_to_contact_page(self, page: Page, website_url: str,
                                      form_validator=None) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Complete workflow with form validation and caching:
        1. Check cache for previously successful URL
        2. Load homepage, find ALL contact links
        3. Try each contact link until we find one with a good form
        4. Cache successful discovery

        Args:
            page: Playwright page object
            website_url: Website base URL
            form_validator: Optional function to validate form quality
                          Should return (success: bool, form_data: dict)

        Returns:
            Tuple of (contact_url, form_data) if successful, (None, None) otherwise
        """

        try:
            # Check cache first
            if self.cache:
                cached_entry = self.cache.get_contact_url(website_url)
                if cached_entry and cached_entry.has_form:
                    self.logger.info(f"Using cached contact URL: {cached_entry.contact_url}")
                    # Navigate to cached URL
                    await page.goto(cached_entry.contact_url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(2)

                    # Validate form still exists
                    if form_validator:
                        self.logger.debug("Validating cached URL form...")
                        success, form_data = await form_validator(page)
                        self.logger.debug(f"Cached URL validation result: success={success}, form_data={form_data}")
                        if success:
                            self.cache.increment_success_count(website_url)
                            return (cached_entry.contact_url, form_data)
                        else:
                            self.logger.warning("Cached URL no longer has valid form, will re-discover")

            # Load homepage first
            contact_urls = None
            homepage_loaded = False

            try:
                self.logger.info(f"Loading homepage: {website_url}")
                await page.goto(website_url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)  # Let JavaScript load
                homepage_loaded = True

                # Find ALL contact URLs
                self.logger.debug("Searching for contact URLs...")
                contact_urls = await self.find_contact_url(page, website_url, find_all=True)
                self.logger.debug(f"find_contact_url returned: {contact_urls} (type: {type(contact_urls)})")

            except Exception as e:
                self.logger.warning(f"Homepage failed to load: {str(e)}")
                self.logger.info("Will try common contact URL patterns directly...")

            # If homepage failed OR no URLs found, try common patterns directly
            if not contact_urls:
                self.logger.info("Trying common contact URL patterns directly...")
                contact_urls = await self._try_common_patterns_direct(website_url, page, form_validator)

            if not contact_urls:
                self.logger.warning("No contact pages found after all strategies")
                return (None, None)

            # If returned a single URL (string), convert to list
            if isinstance(contact_urls, str):
                contact_urls = [contact_urls]

            self.logger.info(f"Found {len(contact_urls)} potential contact URLs to try: {contact_urls}")

            # Try each contact URL until we find one with a good form
            for idx, contact_url in enumerate(contact_urls):
                self.logger.info(f"Trying contact URL [{idx+1}/{len(contact_urls)}]: {contact_url}")

                try:
                    # Navigate to contact page
                    self.logger.debug(f"Navigating to {contact_url}...")
                    await page.goto(contact_url, wait_until="domcontentloaded", timeout=15000)
                    await asyncio.sleep(2)

                    # Validate form if validator provided
                    if form_validator:
                        self.logger.debug(f"Calling form validator on {contact_url}...")
                        success, form_data = await form_validator(page)
                        self.logger.debug(f"Validator returned: success={success}, form_data={form_data}")

                        if success:
                            self.logger.info(f"✅ Found valid contact form at: {contact_url}")
                            self.logger.info(f"   Form has {form_data.get('field_count', 0)} fields")

                            # Cache this successful URL
                            if self.cache and form_data:
                                self.cache.add_contact_url(
                                    website=website_url,
                                    contact_url=contact_url,
                                    has_form=True,
                                    field_count=form_data.get('field_count', 0),
                                    field_types=form_data.get('field_types', []),
                                    form_type=form_data.get('form_type')
                                )

                            return (contact_url, form_data)
                        else:
                            self.logger.warning(f"Validator returned False - page has weak/no form, trying next URL...")
                    else:
                        # No validator, accept first page
                        return (contact_url, None)

                except Exception as e:
                    self.logger.warning(f"Failed to load/validate {contact_url}: {str(e)}")
                    continue

            self.logger.warning("No contact pages with valid forms found after trying all URLs")
            return (None, None)

        except Exception as e:
            self.logger.error(f"Error navigating to contact page: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return (None, None)
