# Repository Guidelines

## Project Structure & Module Organization
- Core Playwright automation flows live in `src/automation/` (detectors inside `forms/`), domain schemas in `src/models/`, and shared helpers in `src/utils/`.
- Root scripts like `final_retest_with_contact_urls.py` orchestrate batches; generated metrics land in timestamped folders under `tests/` and `logs/`.
- The frontend dashboard lives in `frontend/` (Vite + React), with architectural docs and run books in `docs/` and curated `*.md` files at the root.
- Configuration starts with `config/logging.yml`; secrets stay in a local `.env`.

## Build, Test, and Development Commands
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python final_retest_with_contact_urls.py   # batch automation
pytest                                     # Python checks
```
```bash
cd frontend
npm install
npm run dev        # Vite server
npm run build      # production bundle
npm run test       # Vitest + RTL
```

## Coding Style & Naming Conventions
- Format Python with Black (88 cols) and isort; enforce type hints, 4-space indentation, and snake_case for functions and modules.
- Detector classes and service objects are PascalCase; async helpers end with `_async`, constants use SCREAMING_SNAKE_CASE.
- Run `flake8`, `mypy`, and `black --check` before committing Python changes; rely on ESLint/Prettier defaults in `frontend/` and keep React components PascalCase with colocated `.test.tsx` files.

## Testing Guidelines
- House quick unit coverage in `tests/unit/` and workflow scenarios in `tests/integration/`; keep persisted batch outputs in timestamped folders to preserve historical baselines.
- Follow PyTest discovery (`test_*.py`, `Test*`, `test_*`) and reuse fixtures from `tests/fixtures/` for Playwright setup.
- Execute `pytest -k <keyword>` during development, then `pytest --maxfail=1` before pushing; run `npm run test` or `npm run test:coverage` when touching the dashboard.

## Commit & Pull Request Guidelines
- Write imperative commit subjects under 72 chars (e.g., `Tighten gravity form fallback`) and keep unrelated changes separate.
- Mention impacted scripts or data sources in the body (`Affects: src/automation/forms/form_detector.py`) and note any manual steps taken.
- Pull requests must include a scenario summary, linked issue, relevant screenshots/metrics, and the exact commands executed; ping the automation or frontend owner depending on the surface touched.

## Security & Configuration Tips
- Never commit `.env` files or raw dealership CSVs from `data/`; scrub URLs or VINs before sharing logs.
- Update `config/logging.yml` instead of hard-coding handlers, and rotate stealth headers or API keys during deploys.
