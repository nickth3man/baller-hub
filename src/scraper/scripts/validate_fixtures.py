"""Validate basketball-reference fixtures against HTML rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from src.scraper.utils.fixture_validation import (
    build_validation_context,
    validate_fixture_html,
)

DEFAULT_MANIFEST = Path("scripts/fixture_manifest.json")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to fixture manifest JSON.",
    )
    parser.add_argument(
        "--validator",
        action="append",
        default=[],
        help="Validator key to include (repeatable).",
    )
    parser.add_argument(
        "--phase",
        action="append",
        default=[],
        help="Fixture phase to include (repeatable).",
    )
    return parser.parse_args(list(argv))


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    base_dir = Path(data.get("output_dir", "tests/integration/files"))
    validator_filter = set(args.validator)
    phase_filter = set(args.phase)

    failures: list[str] = []
    fixtures = data.get("fixtures", [])
    for fixture in fixtures:
        validator_key = fixture.get("validator")
        fixture_phase = fixture.get("phase")
        if validator_filter and validator_key not in validator_filter:
            continue
        if phase_filter and fixture_phase not in phase_filter:
            continue

        fixture_path = base_dir / fixture["fixture_path"]
        if not fixture_path.exists():
            failures.append(f"missing_fixture: {fixture_path.as_posix()}")
            continue

        content = fixture_path.read_bytes()
        if not validator_key:
            failures.append(f"missing_validator: {fixture_path.as_posix()}")
            continue

        errors = validate_fixture_html(content, validator_key)
        if errors:
            context = build_validation_context(content, validator_key)
            failures.append(
                f"{fixture_path.as_posix()}: " + "; ".join(errors)
            )
            failures.append(f"{fixture_path.as_posix()}: context={context}")

    if failures:
        print("Fixture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print("All fixtures validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
