import json
from pathlib import Path

import pytest

from trading.legacy.legacy_experiments import (
    LegacyInventoryError,
    scan_legacy_experiments,
    validate_legacy_inventory,
)


def _package(root: Path, name: str) -> None:
    path = root / name
    path.mkdir(parents=True)
    (path / "__init__.py").write_text("", encoding="utf-8")


def _inventory(path: Path, packages: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": 1, "packages": packages}),
        encoding="utf-8",
    )


def test_legacy_inventory_allows_only_monotonic_removal(tmp_path: Path) -> None:
    root = tmp_path / "legacy" / "experiments"
    _package(root, "old_one")
    _package(root, "old_two")
    inventory = tmp_path / "inventory.json"
    _inventory(inventory, ["old_one", "old_two"])

    assert scan_legacy_experiments(root) == ("old_one", "old_two")
    assert validate_legacy_inventory(inventory, root) == ()

    (root / "old_two" / "__init__.py").unlink()
    assert validate_legacy_inventory(inventory, root) == ()


def test_legacy_inventory_rejects_addition_and_rename_evasion(tmp_path: Path) -> None:
    root = tmp_path / "legacy" / "experiments"
    _package(root, "old_one")
    inventory = tmp_path / "inventory.json"
    _inventory(inventory, ["old_one"])

    _package(root, "new_one")
    assert validate_legacy_inventory(inventory, root) == (
        "new legacy experiment identity is forbidden: new_one",
    )

    (root / "old_one").rename(root / "renamed_old_one")
    assert set(validate_legacy_inventory(inventory, root)) == {
        "new legacy experiment identity is forbidden: new_one",
        "new legacy experiment identity is forbidden: renamed_old_one",
    }


def test_legacy_inventory_rejects_malformed_baseline(tmp_path: Path) -> None:
    root = tmp_path / "legacy" / "experiments"
    root.mkdir(parents=True)
    inventory = tmp_path / "inventory.json"
    _inventory(inventory, ["duplicate", "duplicate"])

    with pytest.raises(LegacyInventoryError, match="unique sorted strings"):
        validate_legacy_inventory(inventory, root)
