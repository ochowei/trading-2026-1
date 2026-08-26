"""Immutable publication boundary for data-access migration results."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from trading.research_data.artifacts import canonical_json_bytes, publish_immutable
from trading.research_data.parity import MigrationParityEvidenceError, MigrationParityStore
from trading.research_data.paths import ResultPathMigrationError, resolve_result_path

MIGRATION_RESULT_SCHEMA_VERSION = 1
MIGRATION_RESULT_SUFFIX = ".migration-result.json"


class MigrationResultError(ValueError):
    """A migration result cannot cross the immutable historical boundary."""


class MigrationResultStore:
    """Publish migration output without making it a current research result."""

    @staticmethod
    def write(
        result: Mapping[str, object],
        *,
        experiment_name: str,
        parity_path: Path,
        path: Path,
    ) -> Path:
        """Write one parity-linked migration result at a deterministic immutable path."""
        try:
            resolved_parity_path = resolve_result_path(Path(parity_path))
        except ResultPathMigrationError as exc:
            raise MigrationResultError(str(exc)) from exc
        parity = _load_parity(resolved_parity_path)
        normalized = _build_payload(
            result,
            experiment_name=experiment_name,
            parity=parity,
            parity_path=resolved_parity_path,
        )
        destination = Path(path)
        _validate_destination(
            destination,
            experiment_name=normalized["experiment_name"],
            snapshot_id=normalized["snapshot_id"],
        )
        if resolved_parity_path.parent.resolve() != destination.parent.resolve():
            raise MigrationResultError(
                "migration parity evidence must be beside the migration result"
            )
        content = canonical_json_bytes(normalized)
        publish_immutable(destination, content, _sha256(content))
        return destination

    @staticmethod
    def load(path: Path) -> dict[str, object]:
        """Read, canonicalize, and re-verify one migration result envelope."""
        requested = Path(path)
        try:
            source = resolve_result_path(requested)
        except ResultPathMigrationError as exc:
            raise MigrationResultError(f"invalid migration result artifact: {exc}") from exc
        if not source.name.endswith(MIGRATION_RESULT_SUFFIX):
            raise MigrationResultError("migration result path must end with .migration-result.json")
        try:
            content = source.read_bytes()
            payload = json.loads(content)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            raise MigrationResultError(f"invalid migration result artifact: {exc}") from exc
        normalized = _validate_payload(payload, source=source)
        if canonical_json_bytes(normalized) != content:
            raise MigrationResultError("migration result artifact is not canonically serialized")
        return normalized


def _build_payload(
    result: Mapping[str, object],
    *,
    experiment_name: str,
    parity: Mapping[str, object],
    parity_path: Path,
) -> dict[str, object]:
    if not _safe_name(experiment_name):
        raise MigrationResultError("experiment_name must be one safe path segment")
    if not isinstance(result, Mapping):
        raise MigrationResultError("migration result must be an object")
    if result.get("schema_version") != 3:
        raise MigrationResultError("migration result must embed result schema version 3")
    snapshot_id = result.get("data_snapshot_id")
    definition_fingerprint = result.get("definition_fingerprint")
    definition_snapshot_id = result.get("definition_snapshot_id")
    if not _digest(snapshot_id):
        raise MigrationResultError("migration result snapshot identity is invalid")
    if not _digest(definition_fingerprint):
        raise MigrationResultError("migration result definition fingerprint is invalid")
    if not _digest(definition_snapshot_id):
        raise MigrationResultError("migration result definition snapshot identity is invalid")
    if result.get("run_mode") != "migration":
        raise MigrationResultError("migration result must declare run_mode migration")
    validity = result.get("validity")
    if not isinstance(validity, Mapping) or validity.get("status") != "migration-pending":
        raise MigrationResultError("migration result must be marked migration-pending")
    metadata = result.get("metadata")
    reproducibility = metadata.get("reproducibility") if isinstance(metadata, Mapping) else None
    if (
        not isinstance(reproducibility, Mapping)
        or reproducibility.get("run_mode") != "migration"
        or reproducibility.get("requalification_required") is not True
    ):
        raise MigrationResultError("migration result reproducibility metadata is incomplete")
    definitions = parity.get("definitions")
    if not isinstance(definitions, Mapping):  # pragma: no cover - parity store validates
        raise MigrationResultError("migration parity definitions are malformed")
    if parity.get("experiment_name") != experiment_name:
        raise MigrationResultError("migration parity experiment does not match result")
    if parity.get("snapshot_id") != snapshot_id:
        raise MigrationResultError("migration parity snapshot does not match result")
    if parity.get("passed") is not True:
        raise MigrationResultError("migration result requires passing parity evidence")
    if reproducibility.get("migration_parity_digest") != parity.get("parity_digest"):
        raise MigrationResultError("migration result parity digest is not linked in metadata")
    if definitions.get("migrated") not in {definition_fingerprint, definition_snapshot_id}:
        raise MigrationResultError("migration result definition does not match parity evidence")
    parity_name = f"{snapshot_id}.migration-parity.json"
    if parity_path.name != parity_name:
        raise MigrationResultError("migration parity path does not match result snapshot")
    if Path(str(reproducibility.get("migration_parity_artifact", ""))).name != parity_name:
        raise MigrationResultError("migration result parity artifact is not linked in metadata")
    return {
        "schema_version": MIGRATION_RESULT_SCHEMA_VERSION,
        "kind": "data-access-migration-result",
        "experiment_name": experiment_name,
        "snapshot_id": snapshot_id,
        "definition_fingerprint": definition_fingerprint,
        "parity_artifact": parity_name,
        "parity_digest": parity["parity_digest"],
        "requalification_required": True,
        "result": copy.deepcopy(dict(result)),
    }


def _validate_payload(payload: object, *, source: Path) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise MigrationResultError("migration result artifact must be an object")
    required = {
        "schema_version",
        "kind",
        "experiment_name",
        "snapshot_id",
        "definition_fingerprint",
        "parity_artifact",
        "parity_digest",
        "requalification_required",
        "result",
    }
    if set(payload) != required:
        raise MigrationResultError("migration result artifact fields are not exact")
    if payload.get("schema_version") != MIGRATION_RESULT_SCHEMA_VERSION:
        raise MigrationResultError("unsupported migration result schema version")
    if payload.get("kind") != "data-access-migration-result":
        raise MigrationResultError("migration result artifact kind is invalid")
    experiment_name = payload.get("experiment_name")
    if not isinstance(experiment_name, str) or not _safe_name(experiment_name):
        raise MigrationResultError("migration result experiment_name is invalid")
    snapshot_id = payload.get("snapshot_id")
    definition_fingerprint = payload.get("definition_fingerprint")
    if not _digest(snapshot_id) or not _digest(definition_fingerprint):
        raise MigrationResultError("migration result identity is invalid")
    _validate_destination(source, experiment_name=experiment_name, snapshot_id=snapshot_id)
    parity_artifact = payload.get("parity_artifact")
    expected_parity_name = f"{snapshot_id}.migration-parity.json"
    if parity_artifact != expected_parity_name:
        raise MigrationResultError("migration result parity artifact identity is invalid")
    if not _digest(payload.get("parity_digest")):
        raise MigrationResultError("migration result parity digest is invalid")
    if payload.get("requalification_required") is not True:
        raise MigrationResultError("migration result must require requalification")
    result = payload.get("result")
    if not isinstance(result, Mapping):
        raise MigrationResultError("migration result embedded result must be an object")
    if (
        result.get("schema_version") != 3
        or result.get("run_mode") != "migration"
        or result.get("data_snapshot_id") != snapshot_id
        or result.get("definition_fingerprint") != definition_fingerprint
    ):
        raise MigrationResultError("migration result embedded result identity is inconsistent")
    if not _digest(result.get("definition_snapshot_id")):
        raise MigrationResultError("migration result embedded definition snapshot is invalid")
    validity = result.get("validity")
    if not isinstance(validity, Mapping) or validity.get("status") != "migration-pending":
        raise MigrationResultError("migration result embedded validity is not migration-pending")
    metadata = result.get("metadata")
    reproducibility = metadata.get("reproducibility") if isinstance(metadata, Mapping) else None
    if (
        not isinstance(reproducibility, Mapping)
        or reproducibility.get("run_mode") != "migration"
        or reproducibility.get("requalification_required") is not True
    ):
        raise MigrationResultError("migration result embedded reproducibility metadata is invalid")
    if Path(str(reproducibility.get("migration_parity_artifact", ""))).name != expected_parity_name:
        raise MigrationResultError("migration result metadata parity artifact is inconsistent")
    parity_path = source.parent / parity_artifact
    try:
        parity = MigrationParityStore.load(parity_path)
    except MigrationParityEvidenceError as exc:
        raise MigrationResultError(
            f"migration result parity evidence cannot be verified: {exc}"
        ) from exc
    if (
        parity.get("experiment_name") != experiment_name
        or parity.get("snapshot_id") != snapshot_id
        or parity.get("passed") is not True
        or parity.get("parity_digest") != payload.get("parity_digest")
        or not isinstance(parity.get("definitions"), Mapping)
        or parity["definitions"].get("migrated")
        not in {
            definition_fingerprint,
            result.get("definition_snapshot_id"),
        }
    ):
        raise MigrationResultError("migration result parity evidence does not match its content")
    if reproducibility.get("migration_parity_digest") != payload.get("parity_digest"):
        raise MigrationResultError("migration result metadata parity digest is inconsistent")
    return dict(payload)


def _validate_destination(destination: Path, *, experiment_name: str, snapshot_id: str) -> None:
    if destination.name != f"{snapshot_id}{MIGRATION_RESULT_SUFFIX}":
        raise MigrationResultError(
            "migration result path must be <snapshot_id>.migration-result.json"
        )
    if destination.parent.name != experiment_name:
        raise MigrationResultError("migration result must be stored under its experiment directory")
    if destination.name == "latest.json":  # pragma: no cover - exact suffix already excludes it
        raise MigrationResultError("migration result cannot replace latest.json")


def _load_parity(path: Path) -> dict[str, object]:
    try:
        return MigrationParityStore.load(path)
    except MigrationParityEvidenceError as exc:
        raise MigrationResultError(f"migration parity evidence cannot be verified: {exc}") from exc


def _safe_name(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and Path(value).name == value
        and value not in {".", ".."}
    )


def _digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
