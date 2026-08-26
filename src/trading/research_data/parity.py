"""Immutable, result-linked data-access migration parity evidence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from trading.research_data.artifacts import canonical_json_bytes, publish_immutable
from trading.research_data.paths import ResultPathMigrationError, resolve_result_path


class MigrationParityEvidenceError(ValueError):
    """A migration parity artifact is malformed or not canonically serialized."""


class MigrationParityStore:
    """Publish and load one immutable migration parity artifact."""

    @staticmethod
    def write(payload: Mapping[str, object], path: Path) -> Path:
        """Write one canonical artifact without replacing different evidence."""
        normalized = _validate_payload(payload)
        destination = Path(path)
        expected_name = f"{normalized['snapshot_id']}.migration-parity.json"
        if destination.name != expected_name:
            raise MigrationParityEvidenceError(
                "migration parity artifact path must be <snapshot_id>.migration-parity.json"
            )
        content = canonical_json_bytes(normalized)
        publish_immutable(destination, content, hashlib.sha256(content).hexdigest())
        return destination

    @staticmethod
    def load(path: Path) -> dict[str, object]:
        """Read and verify one canonical migration parity artifact."""
        requested = Path(path)
        try:
            source = resolve_result_path(requested)
        except ResultPathMigrationError as exc:
            raise MigrationParityEvidenceError(f"invalid migration parity artifact: {exc}") from exc
        if not source.name.endswith(".migration-parity.json"):
            raise MigrationParityEvidenceError(
                "migration parity artifact path must end with .migration-parity.json"
            )
        try:
            content = source.read_bytes()
            payload = json.loads(content)
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            raise MigrationParityEvidenceError(f"invalid migration parity artifact: {exc}") from exc
        normalized = _validate_payload(payload)
        if source.name != f"{normalized['snapshot_id']}.migration-parity.json":
            raise MigrationParityEvidenceError("migration parity path does not match snapshot_id")
        if canonical_json_bytes(normalized) != content:
            raise MigrationParityEvidenceError(
                "migration parity artifact is not canonically serialized"
            )
        return normalized


def _validate_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise MigrationParityEvidenceError("migration parity artifact must be an object")
    required = {
        "schema_version",
        "experiment_name",
        "detector_identity",
        "snapshot_id",
        "result_fingerprint",
        "definitions",
        "runtime",
        "outputs",
        "result",
        "passed",
        "parity_digest",
    }
    if set(payload) != required:
        raise MigrationParityEvidenceError("migration parity artifact fields are not exact")
    if payload["schema_version"] != 1:
        raise MigrationParityEvidenceError("unsupported migration parity schema version")
    for field in ("experiment_name", "detector_identity"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise MigrationParityEvidenceError(f"{field} must be non-empty text")
    for field in ("snapshot_id", "result_fingerprint", "parity_digest"):
        value = payload[field]
        if not isinstance(value, str) or not _is_digest(value):
            raise MigrationParityEvidenceError(f"{field} must be a lowercase SHA-256 digest")
    definitions = payload["definitions"]
    if (
        not isinstance(definitions, Mapping)
        or set(definitions) != {"legacy", "migrated"}
        or any(not isinstance(value, str) or not value.strip() for value in definitions.values())
    ):
        raise MigrationParityEvidenceError("migration parity definitions are incomplete")
    if not isinstance(payload["runtime"], Mapping):
        raise MigrationParityEvidenceError("migration parity runtime must be an object")
    outputs = payload["outputs"]
    if not isinstance(outputs, Mapping) or set(outputs) != {"legacy", "migrated"}:
        raise MigrationParityEvidenceError("migration parity outputs are incomplete")
    for name in ("legacy", "migrated"):
        output = outputs[name]
        if not isinstance(output, Mapping) or set(output) != {"checksum", "layers"}:
            raise MigrationParityEvidenceError(f"{name} output evidence is incomplete")
        if not isinstance(output["checksum"], str) or not _is_digest(output["checksum"]):
            raise MigrationParityEvidenceError(f"{name} output checksum is invalid")
        layers = output["layers"]
        if not isinstance(layers, Mapping) or set(layers) != {"indicators", "signals", "trades"}:
            raise MigrationParityEvidenceError(f"{name} output layer evidence is incomplete")
        if any(not isinstance(value, str) or not _is_digest(value) for value in layers.values()):
            raise MigrationParityEvidenceError(f"{name} output layer checksum is invalid")
    if not isinstance(payload["result"], Mapping):
        raise MigrationParityEvidenceError("migration parity result must be an object")
    if not isinstance(payload["passed"], bool):
        raise MigrationParityEvidenceError("migration parity passed field must be boolean")
    body = dict(payload)
    body.pop("parity_digest")
    expected = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    if payload["parity_digest"] != expected:
        raise MigrationParityEvidenceError("migration parity digest does not match its content")
    return dict(payload)


def _is_digest(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)
