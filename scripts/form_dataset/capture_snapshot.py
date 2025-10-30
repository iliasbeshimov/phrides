"""Capture dealership contact page snapshots for offline form detection tests."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from enhanced_stealth_browser_config import EnhancedStealthBrowserManager

FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "form_detection"
INDEX_PATH = FIXTURE_ROOT / "dataset_index.json"


async def _capture_page(url: str, html_path: Path, screenshot_path: Path, wait: float, capture_screenshot: bool) -> Dict[str, Any]:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    manager = EnhancedStealthBrowserManager()
    async with async_playwright() as playwright_instance:
        browser, context = await manager.open_context(playwright_instance)
        page = await manager.create_enhanced_stealth_page(context)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            if wait:
                await asyncio.sleep(wait)
            try:
                await page.wait_for_load_state("networkidle", timeout=60000)
            except PlaywrightTimeoutError:
                pass

            html = await page.content()
            title = await page.title()
            html_path.write_text(html, encoding="utf-8")
            if capture_screenshot:
                await page.screenshot(path=str(screenshot_path), full_page=True)

            return {
                "url": url,
                "html_path": str(html_path.relative_to(ROOT)),
                "screenshot_path": str(screenshot_path.relative_to(ROOT)),
                "title": title,
            }
        finally:
            await page.close()
            await manager.close_context(browser, context)


def _load_index() -> Dict[str, Any]:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Dataset index missing at {INDEX_PATH}")
    data = json.loads(INDEX_PATH.read_text())
    entries = {entry["slug"]: entry for entry in data.get("entries", [])}
    return {"meta": data, "entries": entries}


def _resolve_output_paths(slug: str) -> Dict[str, Path]:
    page_dir = FIXTURE_ROOT / "pages" / slug
    html_path = page_dir / "contact.html"
    screenshot_path = FIXTURE_ROOT / "screenshots" / f"{slug}.png"
    return {"html": html_path, "screenshot": screenshot_path}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture dealership contact page snapshot")
    parser.add_argument("slug", help="Dealer slug as defined in dataset_index.json")
    parser.add_argument("--url", help="Override contact URL", default=None)
    parser.add_argument("--wait", type=float, default=3.0, help="Extra seconds to wait before capture")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip screenshot capture")
    parser.add_argument("--silent", action="store_true", help="Reduce console output")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    dataset = _load_index()
    entry = dataset["entries"].get(args.slug)
    if not entry:
        raise SystemExit(f"Unknown slug '{args.slug}'. Available: {', '.join(dataset['entries'].keys())}")

    url = args.url or entry["contact_url"]
    paths = _resolve_output_paths(args.slug)

    if not args.silent:
        print(f"Fetching {url}\n  html -> {paths['html']}\n  screenshot -> {paths['screenshot'] if not args.no_screenshot else '[skipped]'}")

    result = await _capture_page(url, paths["html"], paths["screenshot"], args.wait, not args.no_screenshot)

    if not args.silent:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
