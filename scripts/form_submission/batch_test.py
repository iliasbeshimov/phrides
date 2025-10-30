#!/usr/bin/env python3
"""Run form submission runner against multiple dealerships defined in dataset index."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / 'src'
for candidate in (ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.append(str(candidate))

from contact_page_detector import ContactPageDetector
from src.automation.forms.form_submitter import DEFAULT_PLACEHOLDER, FormSubmissionRunner
from src.services.contact.contact_page_cache import ContactPageResolver, ContactPageStore
from src.services.contact.submission_history import SubmissionHistory

DATASET_INDEX = Path("tests/fixtures/form_detection/dataset_index.json")
CSV_DATASET = Path("Dealerships.csv")


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug


def _build_slug(row: dict, existing: set[str]) -> str:
    base_parts = [
        row.get("dealer_name", ""),
        row.get("city", ""),
        row.get("state", ""),
        row.get("zip_code", ""),
    ]
    base = _slugify(" ".join(part for part in base_parts if part))
    if not base:
        base = _slugify(row.get("website", ""))
    if not base:
        base = "dealer"

    slug = base
    suffix = 2
    while slug in existing:
        slug = f"{base}_{suffix}"
        suffix += 1

    existing.add(slug)
    return slug


def load_csv_entries(existing_slugs: set[str]) -> List[dict]:
    if not CSV_DATASET.exists():
        return []

    entries: List[dict] = []
    with CSV_DATASET.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            homepage = (row.get("website") or "").strip()
            if not homepage:
                continue

            dealer_name = (row.get("dealer_name") or "").strip()
            if not dealer_name:
                dealer_name = homepage

            slug = _build_slug(row, existing_slugs)

            entry = {
                "slug": slug,
                "dealer_name": dealer_name,
                "homepage_url": homepage,
                "website": homepage,
                "contact_url": None,
                "platform_hint": "unknown",
                "status": "unverified",
                "source_csv": str(CSV_DATASET),
                "notes": "Imported from Dealerships.csv",
            }
            entries.append(entry)

    return entries


def load_entries(
    slugs: Iterable[str] | None = None,
    sample_size: int | None = None,
    seed: int | None = None,
    history: SubmissionHistory | None = None,
    include_tried: bool = False,
) -> List[dict]:
    data = json.loads(DATASET_INDEX.read_text())
    entries = list(data.get("entries", []))

    existing_slugs = {
        entry.get("slug")
        for entry in entries
        if entry.get("slug")
    }

    csv_entries = load_csv_entries(existing_slugs)
    entries.extend(csv_entries)
    if slugs:
        slug_set = {slug.strip() for slug in slugs}
        entries = [entry for entry in entries if entry.get("slug") in slug_set]
    if history and not include_tried:
        entries = [
            entry for entry in entries
            if not history.should_skip(entry.get("slug", ""))
        ]
    if sample_size and entries:
        rng = random.Random(seed)
        if sample_size < len(entries):
            entries = rng.sample(entries, sample_size)
    return entries


async def run_batch(entries: list[dict], headless: bool, artifact_root: Path) -> None:
    artifact_root.mkdir(parents=True, exist_ok=True)
    runner = FormSubmissionRunner(headless=headless, screenshot_root=artifact_root)
    contact_store = ContactPageStore()
    detector = ContactPageDetector()
    resolver = ContactPageResolver(
        browser_manager=runner.browser_manager,
        detector=detector,
        store=contact_store,
    )
    summary: list[dict] = []
    history = SubmissionHistory()
    for entry in entries:
        dealer = entry.get("dealer_name") or entry.get("slug")
        url = entry.get("contact_url")
        homepage_url = entry.get("homepage_url") or entry.get("website")
        if not homepage_url and url:
            homepage_url = runner._homepage_from_url(url)
        if not url and not homepage_url:
            print(f"[skip] {dealer}: no contact or homepage URL available")
            continue
        print(f"\n=== {dealer} ===")
        try:
            status = await runner.run(
                dealer,
                url,
                DEFAULT_PLACEHOLDER,
                homepage_url=homepage_url,
                resolver=resolver,
            )
        except LookupError as exc:
            print(f"[warn] {dealer}: resolver failed to locate contact page ({exc})")
            summary.append({
                "dealer": dealer,
                "status": "resolver_failed",
                "error": str(exc),
            })
            await asyncio.sleep(2)
            history.record(entry.get("slug", dealer), "resolver_failed")
            continue

        print(status.to_json())
        summary.append(json.loads(status.to_json()))

        history.record(entry.get("slug", dealer), status.status)

        if status.status == "blocked":
            print("[warn] Blocked by Cloudflare; pausing for 60 seconds before next dealer")
            await asyncio.sleep(60)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    summary_path = artifact_root / f"submission_summary_{timestamp}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n[info] Submission summary saved to {summary_path}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Batch run auto form submission")
    parser.add_argument("--slugs", nargs="*", help="Specific dataset slugs to test")
    parser.add_argument("--random", type=int, help="Randomly select this many dealerships from dataset")
    parser.add_argument("--seed", type=int, help="Random seed for --random selection")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode")
    parser.add_argument("--artifact-root", default="artifacts", help="Output directory root")
    parser.add_argument("--include-tried", action="store_true", help="Do not filter out dealerships attempted recently")
    args = parser.parse_args()

    history = SubmissionHistory()

    entries = load_entries(
        slugs=args.slugs,
        sample_size=args.random,
        seed=args.seed,
        history=history,
        include_tried=args.include_tried,
    )
    if not entries:
        print("No dataset entries selected")
        return

    await run_batch(entries, headless=not args.headful, artifact_root=Path(args.artifact_root))


if __name__ == "__main__":
    asyncio.run(main())
