"""Lightweight stealth configuration for Cloudflare-protected sites.

This implementation focuses on minimal fingerprint changes and behavioral
simulation rather than aggressive feature disabling. It is designed to work in
conjunction with a persistent Chrome/Canary profile and the existing
FormSubmissionRunner pipeline.
"""

from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Optional, Tuple

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from config import Config


_BLOCK_PATTERNS = [
    "sorry, you have been blocked",
    "cloudflare ray id",
    "access denied",
    "attention required",
    "checking your browser before",
]

_STEALTH_INIT_SCRIPT = (
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)


class CloudflareStealth:
    """Helper for opening a headful Chromium session with gentle stealth tweaks."""

    def __init__(
        self,
        user_data_dir: Optional[Path] = None,
        warmup_delay_range: Tuple[float, float] = (1.0, 2.0),
        browser_channel: Optional[str] = None,
    ) -> None:
        resolved_dir = user_data_dir if user_data_dir is not None else Config.AUTO_CONTACT_USER_DATA_DIR
        resolved_channel = browser_channel if browser_channel is not None else Config.AUTO_CONTACT_BROWSER_CHANNEL

        self.user_data_dir = Path(resolved_dir).expanduser() if resolved_dir else None
        self.warmup_delay_range = warmup_delay_range
        self.browser_channel = resolved_channel
        self._playwright: Optional[Playwright] = None

    async def _ensure_playwright(self) -> Playwright:
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def create_stealth_session(
        self,
        playwright: Optional[Playwright] = None,
        *,
        headless: bool = False,
    ) -> Tuple[Optional[Browser], BrowserContext, Page]:
        """Return (browser, context, page) ready for use."""

        if playwright is not None:
            pw = playwright
        else:
            pw = await self._ensure_playwright()

        launch_args = [
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if self.user_data_dir:
            # Persistent contexts behave most naturally in headful mode.
            context = await pw.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                channel=self.browser_channel,
                args=launch_args,
            )
            browser: Optional[Browser] = None
        else:
            browser = await pw.chromium.launch(
                headless=headless,
                channel=self.browser_channel,
                args=launch_args,
            )
            context = await browser.new_context()

        page = await self.create_stealth_page(context)
        return browser, context, page

    async def create_stealth_page(self, context: BrowserContext) -> Page:
        page = await context.new_page()
        await page.add_init_script(_STEALTH_INIT_SCRIPT)
        return page

    async def _create_stealth_page(self, context: BrowserContext) -> Page:
        """Backward-compatible alias for legacy consumers."""
        return await self.create_stealth_page(context)

    async def navigate_with_cloudflare_evasion(
        self,
        page: Page,
        url: str,
        *,
        referrer: Optional[str] = None,
        max_wait_time: int = 45000,
    ) -> bool:
        """Navigate to `url`, optionally via `referrer`, returning False if blocked."""

        try:
            if referrer:
                await page.goto(referrer, wait_until="domcontentloaded", timeout=max_wait_time)
                await asyncio.sleep(random.uniform(*self.warmup_delay_range))

                contact_link = page.locator(f"a[href='{url}']").first
                if await contact_link.count() > 0:
                    await contact_link.hover()
                    await asyncio.sleep(random.uniform(0.4, 0.8))
                    await contact_link.click()
                    await page.wait_for_load_state("domcontentloaded")
                else:
                    await page.goto(url, wait_until="domcontentloaded", timeout=max_wait_time)
            else:
                await page.goto(url, wait_until="domcontentloaded", timeout=max_wait_time)
        except Exception:
            return False

        try:
            body_text = (await page.inner_text("body")).lower()
        except Exception:
            return False

        if any(pattern in body_text for pattern in _BLOCK_PATTERNS):
            return False

        await self._simulate_human_page_behavior(page)
        return True

    async def close_session(self, browser: Optional[Browser], context: BrowserContext) -> None:
        try:
            if context:
                try:
                    await context.close()
                except Exception:
                    pass
            if browser:
                try:
                    if browser.is_connected():
                        await browser.close()
                except Exception:
                    pass
        finally:
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None

    async def _simulate_human_page_behavior(self, page: Page) -> None:
        try:
            await asyncio.sleep(random.uniform(0.6, 1.4))
            await page.evaluate("window.scrollBy({top: window.innerHeight * 0.25, behavior: 'smooth'})")
            await asyncio.sleep(random.uniform(0.8, 1.4))
            await page.evaluate("window.scrollBy({top: -window.innerHeight * 0.1, behavior: 'smooth'})")
            viewport = page.viewport_size or {"width": 1280, "height": 720}
            for _ in range(random.randint(2, 3)):
                x = random.randint(120, viewport["width"] - 120)
                y = random.randint(120, viewport["height"] - 120)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass
