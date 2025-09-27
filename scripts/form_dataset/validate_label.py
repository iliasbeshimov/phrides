"""Validate annotated form labels against the dataset schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "form_detection"
SCHEMA_PATH = FIXTURE_ROOT / "label_schema.json"


class ValidationError(Exception):
    """Represents a human-readable validation problem."""


def _load_schema() -> Dict:
    return json.loads(SCHEMA_PATH.read_text())


def _load_label(path: Path) -> Dict:
    return json.loads(path.read_text())


def _validate_required_keys(label: Dict, errors: List[str]) -> None:
    for key in ("dealer_slug", "contact_url", "expected_fields"):
        if key not in label:
            errors.append(f"Missing required key: {key}")


def _validate_fields(label: Dict, errors: List[str]) -> None:
    fields = label.get("expected_fields", {})
    if not isinstance(fields, dict):
        errors.append("expected_fields must be an object")
        return

    for field_name, spec in fields.items():
        if not isinstance(spec, dict):
            errors.append(f"Field '{field_name}' spec must be an object")
            continue
        selectors = spec.get("selectors", [])
        if not selectors:
            errors.append(f"Field '{field_name}' must define at least one selector")
        elif not all(isinstance(sel, str) for sel in selectors):
            errors.append(f"Field '{field_name}' selectors must be strings")
        if field_name == "phone":
            fmt = spec.get("format", "unknown")
            if fmt not in {"single_field", "triple_split", "double_split", "extension_option", "unknown"}:
                errors.append("Phone field format must be one of the allowed enums")
            segments = spec.get("segments", [])
            if fmt in {"triple_split", "double_split", "extension_option"} and not segments:
                errors.append(f"Field '{field_name}' expected segments for format {fmt}")
            for segment in segments:
                if not isinstance(segment, dict):
                    errors.append("Phone segments must be objects")
                    continue
                if "selectors" not in segment or "order" not in segment:
                    errors.append("Phone segment must include selectors and order")
                if not all(isinstance(sel, str) for sel in segment.get("selectors", [])):
                    errors.append("Phone segment selectors must be strings")


def _validate_paths(label_path: Path, label: Dict, errors: List[str]) -> None:
    html_path = label.get("snapshot_path")
    if html_path:
        full_html = ROOT / html_path
        if not full_html.exists():
            errors.append(f"Snapshot HTML missing: {full_html}")
    screenshot = label.get("screenshot_path")
    if screenshot:
        full_screenshot = ROOT / screenshot
        if not full_screenshot.exists():
            errors.append(f"Screenshot missing: {full_screenshot}")


def validate_label(label_path: Path) -> None:
    schema = _load_schema()
    label = _load_label(label_path)
    errors: List[str] = []

    _validate_required_keys(label, errors)
    _validate_fields(label, errors)
    _validate_paths(label_path, label, errors)

    if errors:
        raise ValidationError("\n".join(errors))

    print(f"Label OK: {label_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a form label JSON file")
    parser.add_argument("label", type=Path, help="Path to label JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        validate_label(args.label)
    except ValidationError as exc:
        print(f"Validation failed for {args.label}:")
        for line in str(exc).splitlines():
            print(f"  - {line}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
