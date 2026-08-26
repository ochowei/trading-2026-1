import hashlib
import json

import pytest

from trading.research_data import (
    ImmutableBlobCorruptionError,
    MigrationParityEvidenceError,
    MigrationParityStore,
)
from trading.research_data.artifacts import canonical_json_bytes


def parity_payload() -> dict[str, object]:
    digest = "a" * 64
    body: dict[str, object] = {
        "schema_version": 1,
        "experiment_name": "spy_007_trend_pullback",
        "detector_identity": "spy_007_trend_pullback",
        "snapshot_id": digest,
        "result_fingerprint": "b" * 64,
        "definitions": {"legacy": "legacy:spy_007", "migrated": "b" * 64},
        "runtime": {"python": "3.11", "dependencies": {"pandas": "2.3.1"}},
        "outputs": {
            "legacy": {
                "checksum": "c" * 64,
                "layers": {
                    "indicators": "d" * 64,
                    "signals": "e" * 64,
                    "trades": "f" * 64,
                },
            },
            "migrated": {
                "checksum": "c" * 64,
                "layers": {
                    "indicators": "d" * 64,
                    "signals": "e" * 64,
                    "trades": "f" * 64,
                },
            },
        },
        "result": {"passed": True, "differences": []},
        "passed": True,
    }
    body["parity_digest"] = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    return body


def test_migration_parity_store_round_trips_canonical_evidence(tmp_path) -> None:
    payload = parity_payload()
    path = MigrationParityStore.write(
        payload,
        tmp_path / "results" / "spy_007_trend_pullback" / (("a" * 64) + ".migration-parity.json"),
    )

    assert MigrationParityStore.load(path) == payload


def test_migration_parity_store_rejects_tampering_and_collisions(tmp_path) -> None:
    payload = parity_payload()
    path = tmp_path / (("a" * 64) + ".migration-parity.json")
    MigrationParityStore.write(payload, path)

    tampered = dict(payload)
    tampered["passed"] = False
    path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(MigrationParityEvidenceError, match="canonical|digest"):
        MigrationParityStore.load(path)

    path.unlink()
    MigrationParityStore.write(payload, path)
    changed = dict(payload)
    changed["experiment_name"] = "other"
    changed["parity_digest"] = hashlib.sha256(
        canonical_json_bytes(
            {key: value for key, value in changed.items() if key != "parity_digest"}
        )
    ).hexdigest()
    with pytest.raises(ImmutableBlobCorruptionError):
        MigrationParityStore.write(changed, path)


def test_migration_parity_store_requires_immutable_path_suffix(tmp_path) -> None:
    with pytest.raises(MigrationParityEvidenceError, match="snapshot_id"):
        MigrationParityStore.write(parity_payload(), tmp_path / "parity.json")
