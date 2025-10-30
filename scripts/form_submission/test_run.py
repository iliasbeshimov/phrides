#!/usr/bin/env python3
"""CLI harness for exercising the form submission runner with placeholder data."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from src.automation.forms.form_submitter import DEFAULT_PLACEHOLDER, FormSubmissionRunner


async def main() -> None:
    parser = argparse.ArgumentParser(description="Test auto form submission for a single dealer")
    parser.add_argument("url", help="Contact form URL")
    parser.add_argument("dealer", help="Dealer name")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode")
    parser.add_argument("--artifact-root", default="artifacts", help="Where to store screenshots/logs")
    args = parser.parse_args()

    runner = FormSubmissionRunner(headless=not args.headful, screenshot_root=Path(args.artifact_root))
    status = await runner.run(args.dealer, args.url, DEFAULT_PLACEHOLDER)

    print("=== Submission Summary ===")
    print(status.to_json())


if __name__ == "__main__":
    asyncio.run(main())
