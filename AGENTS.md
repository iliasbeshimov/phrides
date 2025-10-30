# Repository Guidelines

## Project Structure & Module Organization
- `src/automation/` hosts Playwright flows; detectors sit in `forms/`, support helpers in `src/utils/`, and domain schemas in `src/models/`.
- Batch scripts such as `final_retest_with_contact_urls.py` live at the root and drop metrics plus screenshots into timestamped folders under `tests/` and `logs/`.
- The frontend dashboard runs from `frontend/` (Vite + React); long-form guides stay in `docs/` and curated `*.md` references at the root.
- Configuration loads from `config/logging.yml` and a local `.env`; never hard-code secrets in scripts.

## Build, Test, and Development Commands
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest --maxfail=1
python final_retest_with_contact_urls.py
```
```
cd frontend
npm install
npm run dev
npm run test
npm run build
```
- Use the first block to prep the automation environment; `pytest --maxfail=1` acts as the pre-push gate.
- Run the second block for UI work; `npm run test` executes Vitest + React Testing Library.

## Coding Style & Naming Conventions
- Auto-format Python with Black (88 cols) and isort; keep 4-space indentation, snake_case modules/functions, PascalCase detectors/services, `_async` suffix for coroutines, and SCREAMING_SNAKE_CASE constants.
- Lint backend with `flake8` and `mypy`; JavaScript/TypeScript relies on ESLint + Prettier defaults, with React components in PascalCase and colocated `.test.tsx` files.

## Testing Guidelines
- Place fast unit specs in `tests/unit/` and workflow or Playwright scenarios in `tests/integration/`; reuse fixtures from `tests/fixtures/`.
- Persist batch outputs under timestamped folders inside `tests/` or `logs/` to preserve regression history.
- Filter suites during development via `pytest -k "<keyword>"`; run `npm run test:coverage` when touching dashboard data pipelines.

## Commit & Pull Request Guidelines
- Write imperative subjects under 72 chars (e.g., `Tighten gravity form fallback`) and keep unrelated changes separate.
- Reference impacted files in the body (`Affects: src/automation/forms/form_detector.py`) and list manual steps or data touched.
- PRs must cite the scenario, linked issue, screenshots or metrics, and commands executed; ping automation or frontend owners as appropriate.

## Security & Configuration Tips
- Never commit `.env` files or raw dealership CSVs from `data/`; scrub URLs and VINs before sharing artifacts.
- Extend logging through `config/logging.yml` instead of inline handlers, and rotate stealth headers or API keys every deploy.
