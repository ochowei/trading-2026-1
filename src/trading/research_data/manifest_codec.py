"""Strict canonical codec for immutable research snapshot manifests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime

from trading.market_data import (
    AvailabilityPolicy,
    CoverageMode,
    MarketDataCoveragePolicy,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.research_data.artifacts import canonical_json_bytes
from trading.research_data.models import (
    DataBlobRef,
    DefinitionBlobRef,
    SnapshotDataRef,
    SnapshotManifest,
)


class SnapshotManifestError(RuntimeError):
    """A snapshot manifest is malformed or has a false content identity."""


def manifest_body(
    created_at: datetime,
    decision_time: SignalDecisionTime,
    entries: tuple[SnapshotDataRef, ...],
    definition: DefinitionBlobRef | None,
) -> dict[str, object]:
    """Build canonical manifest content excluding its derived identity."""
    return {
        "schema_version": 1,
        "created_at": _timestamp(created_at),
        "decision_time": {
            "session": decision_time.session.isoformat(),
            "decided_at": _timestamp(decision_time.decided_at),
        },
        "data": [_data_entry_payload(entry) for entry in entries],
        "definition": (
            {
                "digest": definition.digest,
                "byte_count": definition.byte_count,
                "fingerprint": definition.fingerprint,
            }
            if definition is not None
            else None
        ),
    }


def _data_entry_payload(entry: SnapshotDataRef) -> dict[str, object]:
    """Serialize one data entry while preserving old default manifest bytes."""
    payload: dict[str, object] = {
        "series": {
            "provider": entry.series.provider,
            "symbol": entry.series.symbol,
            "interval": entry.series.interval,
            "adjustment_policy": entry.series.adjustment_policy,
        },
        "history_start": entry.history_start.isoformat(),
        "role": entry.role,
        "availability_policy": (
            {
                "publication_lag_sessions": entry.availability_policy.publication_lag_sessions,
                "max_observation_lag_sessions": (
                    entry.availability_policy.max_observation_lag_sessions
                ),
                "publication_time_known": entry.availability_policy.publication_time_known,
            }
            if entry.availability_policy
            else None
        ),
        "data_cutoff": entry.data_cutoff.isoformat(),
        "full_refresh_at": _timestamp(entry.full_refresh_at),
        "blob": {
            "digest": entry.blob.digest,
            "byte_count": entry.blob.byte_count,
            "row_count": entry.blob.row_count,
        },
    }
    if entry.coverage_policy.mode is not CoverageMode.XNYS_SESSIONS:
        payload["coverage_policy"] = entry.coverage_policy.mode.value
    return payload


def manifest_payload(manifest: SnapshotManifest) -> dict[str, object]:
    """Build complete canonical manifest content including identity."""
    return {
        "snapshot_id": manifest.snapshot_id,
        **manifest_body(
            manifest.created_at,
            manifest.decision_time,
            manifest.data,
            manifest.definition,
        ),
    }


def manifest_from_bytes(content: bytes) -> SnapshotManifest:
    """Strictly parse and verify canonical snapshot identity."""
    payload = json.loads(content)
    if not isinstance(payload, dict):
        raise TypeError("snapshot manifest must be a JSON object")
    manifest = _manifest_from_payload(payload)
    if manifest.schema_version != 1:
        raise SnapshotManifestError(
            f"unsupported snapshot manifest schema {manifest.schema_version}"
        )
    expected_id = hashlib.sha256(
        canonical_json_bytes(
            manifest_body(
                manifest.created_at,
                manifest.decision_time,
                manifest.data,
                manifest.definition,
            )
        )
    ).hexdigest()
    if manifest.snapshot_id != expected_id:
        raise SnapshotManifestError("snapshot manifest identity does not match its content")
    if content != canonical_json_bytes(manifest_payload(manifest)):
        raise SnapshotManifestError(
            "snapshot manifest contains unknown fields or non-canonical bytes"
        )
    return manifest


def _manifest_from_payload(payload: dict[str, object]) -> SnapshotManifest:
    decision_payload = payload["decision_time"]
    if not isinstance(decision_payload, dict):
        raise TypeError("decision_time must be an object")
    raw_entries = payload["data"]
    if not isinstance(raw_entries, list):
        raise TypeError("data must be a list")
    entries: list[SnapshotDataRef] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise TypeError("snapshot data entry must be an object")
        raw_series = raw_entry["series"]
        raw_blob = raw_entry["blob"]
        if not isinstance(raw_series, dict) or not isinstance(raw_blob, dict):
            raise TypeError("series and blob must be objects")
        raw_policy = raw_entry["availability_policy"]
        if raw_policy is not None and not isinstance(raw_policy, dict):
            raise TypeError("availability_policy must be an object or null")
        policy = (
            AvailabilityPolicy(
                publication_lag_sessions=_require_int(
                    raw_policy["publication_lag_sessions"],
                    "publication_lag_sessions",
                ),
                max_observation_lag_sessions=_require_int(
                    raw_policy["max_observation_lag_sessions"],
                    "max_observation_lag_sessions",
                ),
                publication_time_known=_require_bool(
                    raw_policy["publication_time_known"],
                    "publication_time_known",
                ),
            )
            if raw_policy is not None
            else None
        )
        raw_coverage = raw_entry.get("coverage_policy", CoverageMode.XNYS_SESSIONS.value)
        coverage = MarketDataCoveragePolicy(_require_str(raw_coverage, "coverage_policy"))
        entries.append(
            SnapshotDataRef(
                series=MarketDataSeries(
                    provider=_require_str(raw_series["provider"], "provider"),
                    symbol=_require_str(raw_series["symbol"], "symbol"),
                    interval=_require_str(raw_series["interval"], "interval"),
                    adjustment_policy=_require_str(
                        raw_series["adjustment_policy"],
                        "adjustment_policy",
                    ),
                ),
                history_start=date.fromisoformat(
                    _require_str(raw_entry["history_start"], "history_start")
                ),
                role=_require_str(raw_entry["role"], "role"),
                availability_policy=policy,
                data_cutoff=date.fromisoformat(
                    _require_str(raw_entry["data_cutoff"], "data_cutoff")
                ),
                full_refresh_at=_parse_timestamp(raw_entry["full_refresh_at"]),
                blob=DataBlobRef(
                    digest=_require_str(raw_blob["digest"], "blob.digest"),
                    byte_count=_require_int(raw_blob["byte_count"], "byte_count"),
                    row_count=_require_int(raw_blob["row_count"], "row_count"),
                ),
                coverage_policy=coverage,
            )
        )
    raw_definition = payload.get("definition")
    if raw_definition is not None and not isinstance(raw_definition, dict):
        raise TypeError("definition must be an object or null")
    definition = (
        DefinitionBlobRef(
            digest=_require_str(raw_definition["digest"], "definition.digest"),
            byte_count=_require_int(raw_definition["byte_count"], "definition.byte_count"),
            fingerprint=_require_str(
                raw_definition["fingerprint"],
                "definition.fingerprint",
            ),
        )
        if raw_definition is not None
        else None
    )
    return SnapshotManifest(
        snapshot_id=_require_str(payload["snapshot_id"], "snapshot_id"),
        schema_version=_require_int(payload["schema_version"], "schema_version"),
        created_at=_parse_timestamp(payload["created_at"]),
        decision_time=SignalDecisionTime(
            session=date.fromisoformat(
                _require_str(decision_payload["session"], "decision_time.session")
            ),
            decided_at=_parse_timestamp(decision_payload["decided_at"]),
        ),
        data=tuple(entries),
        definition=definition,
    )


def _parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise TypeError("timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(UTC)


def _require_bool(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{field} must be a JSON boolean")
    return value


def _require_int(value: object, field: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field} must be a JSON integer")
    return value


def _require_str(value: object, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a JSON string")
    return value


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("snapshot timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
