# Auto Form Submission Overview

## Mission
Build a reusable automation layer that can take normalized contact data and reliably:
1. Load a dealership contact page (including CTA + modal flows).
2. Detect the active form, map required fields, and resolve dropdowns/checkboxes.
3. Populate the form with the provided data, handling edge cases (segmented phone inputs, hidden honeypots, required dropdown choices).
4. Submit the form and capture the outcome (success message, validation errors, unexpected blockers).
5. Emit structured status objects and artifacts (logs + screenshots) for downstream systems (UI, analytics, retry logic).

## Placeholder Contact Data (for testing)
- First name: **Miguel**
- Last name: **Montoya**
- Email: **migueljmontoya@protonmail.com**
- Phone: **650-688-2311**
- Zip code: **90066**
- Message: **"Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available. Best, Miguel"**

## Planned Components
1. **Detection Enhancements**
   - Reuse `EnhancedFormDetector` but add overlay dismissals (cookie banners, chat widgets, modals).
   - After detection failure attempt CTA/modal sequence (`_maybe_trigger_modal_flow`).
   - Provide access to raw form element so submission layer can inspect surrounding DOM.

2. **Form Submission Engine** (`src/automation/forms/form_submitter.py`)
   - `ContactPayload` dataclass for normalized data.
   - `SubmissionStatus` dataclass capturing detection state, filled fields, submission success, errors, and artifact paths.
   - `FormSubmissionRunner` orchestrates:
     1. Launch stealth browser via `EnhancedStealthBrowserManager`.
     2. Run detection; store detection screenshot.
     3. Populate fields (first/last/email/phone/zip/message) using detection output + fallback DOM heuristics.
     4. Handle dropdowns (`Preferred Contact Method`, `Reason`, etc.) and checkboxes (TCPA, marketing consent).
     5. Submit and observe success indicators (`thank you`, `submitted`, form hidden, HTTP nav).
     6. Capture filled + confirmation screenshots.
     7. Return structured status dict.
   - Extensive console logging for each stage.

3. **Field Filling Helpers**
   - `fill_text_field(page, selector, value)` with retry + highlight (optional).
   - `fill_phone_field(page, value)` supporting single field and segmented inputs (detect via DOM patterns).
   - `select_dropdown_option(page, hint_keywords)` to pick Sales/contact preference options.
   - `tick_all_checkboxes(page)` focusing on consent/TCPA boxes.

4. **Obstacle Handling**
   - Cookie banners: click buttons containing `Ok`, `Accept`, `Agree`, `Got it`.
   - Chat widgets: close buttons with `aria-label*='close'` inside `iframe`, or hide container via JS fallback.
   - Modal cleanup after submission (close buttons, overlay removal) so subsequent automation is stable.

5. **Artifacts & Logging**
   - Directory structure: `artifacts/<timestamp>/<slug>/` with `detected.png`, `filled.png`, `submitted.png`, `status.json`, and verbose log text.
   - Status JSON fields: `dealer_name`, `url`, `detection_success`, `fields_filled`, `missing_fields`, `dropdown_choices`, `checkboxes_checked`, `submission_status`, `confirmation_text`, `errors`.

6. **Testing Harness** (`scripts/form_submission/test_run.py`)
   - CLI: `python scripts/form_submission/test_run.py --dealer "Anchorage Chrysler Center" --url https://...`
   - Uses placeholder payload, prints summary, and saves artifacts.
   - Supports `--headful` and `--wait` options for debugging.

## Status Codes & Integration Hooks
- `detection_failed`
- `fields_partial`
- `submission_success`
- `submission_failed`
- `blocked` (CAPTCHA, unexpected modal)

Return object example:
```json
{
  "dealer": "Anchorage Chrysler Center",
  "url": "https://www.anchoragechryslercenter.com/contactus",
  "status": "submission_success",
  "fields_filled": ["first_name", "last_name", "email", "phone", "zip", "message", "preferred_contact"],
  "dropdown_choices": {"Preferred Contact Method": "Text"},
  "checkboxes_checked": ["I consent to receive marketing text messages..."],
  "missing_fields": [],
  "confirmation_text": "Thank you for contacting Anchorage Chrysler Center.",
  "artifacts": {
    "detected": "artifacts/20250927T183500/anchorage_chrysler_center/detected.png",
    "filled": "artifacts/20250927T183500/anchorage_chrysler_center/filled.png",
    "submitted": "artifacts/20250927T183500/anchorage_chrysler_center/submitted.png",
    "log": "artifacts/20250927T183500/anchorage_chrysler_center/run.log"
  },
  "errors": []
}
```

## Integration Notes for Frontend (Claude)
- Back-end CLI can be wrapped in a lightweight API later; for now expect JSON output + artifact paths.
- Provide ability to pass custom payloads (once UI pipeline ready) through a JSON file or STDIN.
- Status JSON designed to drive UI: highlight missing fields, show confirmation text, and decide retries.
- Logs include time-stamped steps so progress indicator can be real-time if hooked to websockets/process streaming.

## Immediate Next Steps
1. Implement `FormSubmissionRunner` + helpers with verbose logging.
2. Expand `_dismiss_cookie_banner` and modal heuristics in `EnhancedFormDetector` to cover chat widgets and multi-step CTAs.
3. Build test harness script and validate against: Anchorage, Capital City CDJR, Rairdons Kirkland, and a baseline Gravity Forms site.
4. Iterate on edge cases (honeypots, validation errors) and document resolutions in this file.



## Latest Test Runs (2025-09-27)
- Anchorage Chrysler Center (modal CTA flow): `submission_success` with dropdown `Text`, marketing consent checked, confirmation "thank you".
- Capital City CDJR (Gravity Forms): fields populated and consent checked; no confirmation message observed (likely additional validation/CAPTCHA) -> reported as `submission_failed`.

Artifacts recorded under `artifacts/<timestamp>/<slug>/` with `detected.png`, `filled.png`, `submitted.png`, `run.log`, and `status.json`.


## Tooling Updates
- **FormSubmissionRunner** (`src/automation/forms/form_submitter.py`) now detects validation errors, handles custom contact dropdowns, and records structured status JSON/artifacts.
- **HTTP Service**: `scripts/form_submission/http_service.py` exposes a `/submit` endpoint (FastAPI) for external clients (UI, CLI) to trigger submissions.
- **Batch Harness**: `scripts/form_submission/batch_test.py` iterates over dataset entries (`dataset_index.json`) using the placeholder payload.
- **CLI Demo**: `scripts/form_submission/test_run.py` remains the quickest way to verify a single dealer.

## Recent Results
- Anchorage Chrysler Center → `submission_success` (modal CTA handled, dropdown "Text", marketing consent checked when available).
- Capital City CDJR → still `submission_failed` (no confirmation detected; likely server-side validation or anti-bot). Error capture now surfaces any inline validation text for diagnosis.

## Next Targets
1. Inspect failing Gravity Forms (e.g., Capital City CDJR) to determine whether additional actions (reCAPTCHA, required reason dropdown) are needed.
2. Expand dropdown mapping once we catalog more department labels (e.g., service, finance) and multi-select widgets.
3. Integrate HTTP service with Claude's UI once endpoints/contract are finalized.
4. Use `batch_test.py` nightly across the dataset to catch regressions as new dealerships are added.


## Human-Like Navigation Module
- Added `src/automation/navigation/human_behaviors.py` providing warm-up behavior (homepage visit, scrolling, timed hovers) before form detection.
- `FormSubmissionRunner` now accepts a `behavior_config` and automatically runs `warm_up_and_navigate` to mimic organic navigation before contacting.
- Logs include `[human]` entries showing each simulated action.

## Testing Checklist (current focus)
1. Re-run `scripts/form_submission/test_run.py` for modal (Anchorage) and Gravity Form (Capital City CDJR) flows after each change.
2. Execute `scripts/form_submission/batch_test.py --slugs anchorage_chrysler_center capital_city_cdjr rairdons_chrysler_kirkland` to ensure broader coverage.
3. Review generated artifacts (`detected.png`, `filled.png`, `submitted.png`, `run.log`) to confirm fields populate correctly and success/validation states are captured.
4. For any `submission_failed`, inspect `run.log` + `status.json` and adjust dropdown/checkbox/error heuristics accordingly.


## Recent Fixes
- **CSS Escaping:** `EnhancedFormDetector._canonical_selector` now uses `CSS.escape` so Dealer.com-style IDs containing dots (e.g., `contact.firstName`) are usable during filling.
- **Dropdown harvesting:** `_collect_selects` in `form_submitter.py` escapes IDs and grabs label text reliably.
- **Block detection:** `FormSubmissionRunner` detects Cloudflare/Access Denied pages and marks runs as `blocked`, capturing a `blocked.png` artifact.
- **Dataset tweak:** `max_curnow_cdjr` contact URL updated to `/contact.htm` (Dealer.com form).

## Validation Status
- Thomas Garage Inc → `blocked` (Cloudflare).
- Max Curnow CDJR → fields filled, custom dropdown chosen (`Phone`), response returned dealer error text (captured in `errors`).
- Larry H. Miller CDJR → fills all fields except zip (not present), dealer returns generic error message (captured).
- Anchorage Chrysler → still `submission_success`.
