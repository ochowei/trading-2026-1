"""Closed-inventory guard for legacy experiment source identities."""

from __future__ import annotations

import json
from pathlib import Path


class LegacyInventoryError(ValueError):
    """The tracked legacy inventory is malformed or has expanded."""


def scan_legacy_experiments(root: Path) -> tuple[str, ...]:
    """Return importable experiment identities from the legacy archive."""
    if not root.is_dir():
        raise LegacyInventoryError(f"legacy experiment root does not exist: {root}")
    return tuple(
        sorted(
            child.name
            for child in root.iterdir()
            if child.is_dir()
            and not child.name.startswith("_")
            and (child / "__init__.py").is_file()
        )
    )


def validate_legacy_inventory(inventory_path: Path, experiment_root: Path) -> tuple[str, ...]:
    """Return deterministic violations while permitting monotonic removals."""
    try:
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LegacyInventoryError(f"cannot read legacy inventory: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "packages"}:
        raise LegacyInventoryError("legacy inventory must contain schema_version and packages")
    if payload["schema_version"] != 1:
        raise LegacyInventoryError("legacy inventory schema_version must be 1")
    packages = payload["packages"]
    if (
        not isinstance(packages, list)
        or not all(isinstance(item, str) and item for item in packages)
        or packages != sorted(set(packages))
    ):
        raise LegacyInventoryError("legacy inventory packages must be unique sorted strings")
    current = scan_legacy_experiments(experiment_root)
    additions = sorted(set(current).difference(packages))
    return tuple(f"new legacy experiment identity is forbidden: {item}" for item in additions)
