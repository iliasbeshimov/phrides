"""Reusable helpers for human-like browsing patterns before form detection/submission."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from playwright.async_api import Page


@dataclass
class HumanBehaviorConfig:
    enable_warmup: bool = True
    scroll_pause_range: tuple[int, int] = (500, 1200)  # milliseconds
    hover_pause_range: tuple[int, int] = (200, 600)
    post_click_wait: int = 800


DEFAULT_BEHAVIOR = HumanBehaviorConfig()


async def warm_up_and_navigate(
    page: Page,
    contact_url: str,
    log_lines: List[str],
    config: HumanBehaviorConfig = DEFAULT_BEHAVIOR,
) -> str:
    """Navigate to the contact page and optionally perform on-page warm-up gestures."""

    await page.goto(contact_url, wait_until="domcontentloaded", timeout=60000)

    if config.enable_warmup:
        log_lines.append("[human] Performing on-page warm-up gestures")
        await _slow_page_view(page, config)
    else:
        await page.wait_for_timeout(_rand_between(config.scroll_pause_range))

    return contact_url


async def _slow_page_view(page: Page, config: HumanBehaviorConfig) -> None:
    await page.wait_for_timeout(_rand_between(config.scroll_pause_range))
    await page.evaluate("window.scrollBy({top: window.innerHeight * 0.3, behavior: 'smooth'})")
    await page.wait_for_timeout(_rand_between(config.scroll_pause_range))
    await page.evaluate("window.scrollBy({top: -window.innerHeight * 0.15, behavior: 'smooth'})")
    await page.wait_for_timeout(_rand_between(config.scroll_pause_range))


def _rand_between(bounds: tuple[int, int]) -> int:
    return random.randint(bounds[0], bounds[1])
