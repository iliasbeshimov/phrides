# Claude Handoff – 28 Sep 2025

## Context
- We are automating contact form submissions for Chrysler/Dodge/Jeep/Ram dealerships using Playwright.
- Cloudflare defenses have been the main blocker; recent work focused on maintaining human-like navigation and leveraging a real Chrome Canary profile.

## Latest Work (today)
- **Cloudflare navigation**: Removed the old homepage "warm-up" that caused unnecessary contact→homepage→contact loops. The Cloudflare helper now tries a direct load first and only falls back to a homepage referrer if the direct attempt fails.
- **Stealth session tuning**: `CloudflareStealth` now respects `Config.AUTO_CONTACT_USER_DATA_DIR` and `Config.AUTO_CONTACT_BROWSER_CHANNEL`, so we can run against the user's Chrome Canary profile.
- **Form submitter wiring**: `FormSubmissionRunner` instantiates `CloudflareStealth` with those config values. Headful runs should now open Canary with the user's history, extensions, and cookies.
- **Dataset expansion**: `scripts/form_submission/batch_test.py` merges the curated JSON fixtures with every dealership in `Dealerships.csv`, yielding ~2.3k entries for random sampling. This reduces the risk of Cloudflare learning a tiny set of URLs.
- **Contributor guide**: `AGENTS.md` added to summarize repo layout, commands, coding standards, and security tips for new agents.

## Current State / How to Run
1. Set these in `.env` (already documented to the user):
   ```
   AUTO_CONTACT_USER_DATA_DIR=/Users/iliasbeshimov/Library/Application Support/Google/Chrome Canary
   AUTO_CONTACT_BROWSER_CHANNEL=chrome-canary
   ```
   Reload the shell (`source .env`).
2. Optional: verify via
   ```bash
   python - <<'PY'
   from config import Config
   print(Config.AUTO_CONTACT_USER_DATA_DIR)
   print(Config.AUTO_CONTACT_BROWSER_CHANNEL)
   PY
   ```
3. Run a batch test (headful so Cloudflare sees real UI):
   ```bash
   python scripts/form_submission/batch_test.py --headful --random 5 --seed 937
   ```
   - Entries now come from both `tests/fixtures/form_detection/dataset_index.json` and the full CSV.
   - Contact warm-up stays on the form once loaded; expect fewer detection blocks.

## Known Gaps / Next Steps
- Confirm Canary path and channel work on CI or other machines; fall back gracefully if not available.
- Watch for blocks despite the navigation fix; if they persist, log the URLs and inspect Cloudflare challenges.
- Consider rate limiting / pauses between dealerships to avoid Cloudflare rate detection.
- Revisit `SubmissionHistory` filtering if certain dealers need repeated retests.

## Helpful Paths
- Navigation behavior: `src/automation/navigation/human_behaviors.py`
- Cloudflare session helper: `src/automation/browser/cloudflare_stealth_config.py`
- Batch runner: `scripts/form_submission/batch_test.py`
- Contact resolver cache: `src/services/contact/contact_page_cache.py`

Ping if you need canvas: artifacts of today’s run live under `artifacts/20250928T193357Z/`.
