"""Reject additions or rename-based replacements in the closed legacy experiment tree."""

from __future__ import annotations

import argparse
from pathlib import Path

from trading.core.legacy_experiments import (
    LegacyInventoryError,
    validate_legacy_inventory,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("ci/legacy-experiment-inventory.json"),
    )
    parser.add_argument(
        "--experiments",
        type=Path,
        default=Path("legacy/experiments"),
    )
    args = parser.parse_args()
    try:
        issues = validate_legacy_inventory(args.inventory, args.experiments)
    except LegacyInventoryError as exc:
        raise SystemExit(str(exc)) from exc
    if issues:
        raise SystemExit("\n".join(issues))
    print("legacy experiment inventory passed")


if __name__ == "__main__":
    main()
