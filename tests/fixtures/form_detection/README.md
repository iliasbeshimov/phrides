# Form Detection Regression Dataset

This fixture set stores static dealership contact pages and curated labels so the detector can be evaluated offline.

## Directory Layout
- `dataset_index.json` — master list of dealerships to capture and annotate.
- `pages/<dealer_slug>/contact.html` — saved HTML snapshot for the contact page.
- `screenshots/<dealer_slug>.png` — visual reference captured alongside the HTML.
- `labels/<dealer_slug>.json` — ground-truth selectors, metadata, and field expectations.
- `label_schema.json` — JSON Schema describing the annotation contract.
- `labels/template.json` — quick-start template for new annotations.

## Workflow
1. Run the capture script (see `scripts/form_dataset/capture_snapshot.py`) with a dealer slug from the index to save the HTML and screenshot.
2. Duplicate `labels/template.json`, adjust selectors/segments, and set `last_verified_at` to the current timestamp.
3. Validate the annotation against the schema:
   ```bash
   python scripts/form_dataset/validate_label.py labels/<dealer_slug>.json
   ```
4. Execute the regression harness to compare detected fields against the labels.

Keep snapshots up to date by re-capturing whenever a website changes. Record updates by bumping the `last_verified_at` field and documenting context in the index notes.
