"""Versioned persisted-result schema and read-only validity classification."""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from trading.market_data import PrimaryUSSessionCalendar, SessionCalendar
from trading.research_data.models import DefinitionBlobRef, SnapshotManifest
from trading.research_data.store import ResearchDataStore

CURRENT_RESULT_SCHEMA_VERSION = 2


class ResultValidityStatus(StrEnum):
    """The decision-grade status of one persisted research result."""

    VALID = "valid"
    DATA_STALE = "data-stale"
    DEFINITION_STALE = "definition-stale"
    UNREPRODUCIBLE = "unreproducible"
    LEGACY = "legacy"


@dataclass(frozen=True, slots=True)
class ResultValidity:
    """A status and explanatory reasons computed without mutating the result."""

    status: ResultValidityStatus
    reasons: tuple[str, ...] = ()

    @property
    def is_qualifiable(self) -> bool:
        """Whether the result may be considered by a current qualification workflow."""
        return self.status is ResultValidityStatus.VALID


@dataclass(frozen=True, slots=True)
class ResearchResult:
    """A JSON result plus its computed, non-persisting validity view."""

    payload: dict[str, object]
    validity: ResultValidity

    @property
    def schema_version(self) -> int | None:
        value = self.payload.get("schema_version")
        return value if isinstance(value, int) else None


class ResultSchemaError(RuntimeError):
    """A result cannot be parsed as a JSON object or supported schema."""


def build_result_payload(
    produced: Mapping[str, object],
    *,
    manifest: SnapshotManifest,
    manifest_path: Path,
    run_mode: str,
) -> dict[str, object]:
    """Attach the Phase 3 schema and immutable evidence to one runner output."""
    if manifest.definition is None:
        raise ResultSchemaError("persisted result requires a research-definition snapshot")

    payload = copy.deepcopy(dict(produced))
    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ResultSchemaError("research result metadata must be an object")

    legacy_parts = payload.get("legacy_period_results")
    if not isinstance(legacy_parts, dict):
        legacy_parts = {
            key: copy.deepcopy(payload[key])
            for key in ("part_a", "part_b", "part_c")
            if key in payload
        }

    definition = manifest.definition
    reproducibility = metadata.get("reproducibility", {})
    if not isinstance(reproducibility, dict):
        reproducibility = {}
    reproducibility.update(
        {
            "snapshot_id": manifest.snapshot_id,
            "snapshot_manifest": str(Path(manifest_path)),
            "definition_snapshot_id": definition.digest,
            "definition_fingerprint": definition.fingerprint,
            "run_mode": run_mode,
        }
    )
    metadata["reproducibility"] = reproducibility

    payload.update(
        {
            "schema_version": CURRENT_RESULT_SCHEMA_VERSION,
            "validity": {"status": ResultValidityStatus.VALID.value, "reasons": []},
            "data_snapshot_id": manifest.snapshot_id,
            "data_snapshot_manifest": str(Path(manifest_path)),
            "data_cutoff": manifest.decision_time.session.isoformat(),
            "definition_snapshot_id": definition.digest,
            "definition_fingerprint": definition.fingerprint,
            "development_summary": copy.deepcopy(payload.get("development_summary", {})),
            "historical_stability_folds": copy.deepcopy(
                payload.get("historical_stability_folds", [])
            ),
            "shadow_evidence": copy.deepcopy(payload.get("shadow_evidence", {})),
            "live_evidence": copy.deepcopy(payload.get("live_evidence", {})),
            "legacy_period_results": legacy_parts,
            "metadata": metadata,
            "run_mode": run_mode,
        }
    )
    return payload


def load_result(
    path: Path,
    *,
    store: ResearchDataStore | None = None,
    current_definition_fingerprint: str | DefinitionBlobRef | None = None,
    now: datetime | None = None,
    calendar: SessionCalendar | None = None,
) -> ResearchResult:
    """Read a result and compute status without changing the file or evidence store."""
    result_path = Path(path)
    try:
        loaded = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultSchemaError(f"cannot read result {result_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ResultSchemaError("research result must be a JSON object")
    payload = copy.deepcopy(loaded)
    validity = classify_result(
        payload,
        store=store,
        result_path=result_path,
        current_definition_fingerprint=current_definition_fingerprint,
        now=now,
        calendar=calendar,
    )
    return ResearchResult(payload=payload, validity=validity)


def classify_result(
    payload: Mapping[str, object],
    *,
    store: ResearchDataStore | None = None,
    result_path: Path | None = None,
    current_definition_fingerprint: str | DefinitionBlobRef | None = None,
    now: datetime | None = None,
    calendar: SessionCalendar | None = None,
) -> ResultValidity:
    """Classify a result from actual retained evidence and current definition identity."""
    schema_version = payload.get("schema_version")
    if schema_version is None or schema_version == 1:
        return ResultValidity(ResultValidityStatus.LEGACY, ("result has no Phase 3 evidence",))
    if schema_version != CURRENT_RESULT_SCHEMA_VERSION:
        return ResultValidity(
            ResultValidityStatus.UNREPRODUCIBLE,
            (f"unsupported result schema version: {schema_version}",),
        )
    if declares_incomplete_result(payload):
        return ResultValidity(
            ResultValidityStatus.UNREPRODUCIBLE,
            ("result declares a failed or incomplete execution",),
        )

    required_fields = (
        "validity",
        "data_snapshot_id",
        "data_snapshot_manifest",
        "data_cutoff",
        "definition_snapshot_id",
        "definition_fingerprint",
        "development_summary",
        "historical_stability_folds",
        "shadow_evidence",
        "live_evidence",
        "legacy_period_results",
        "run_mode",
    )
    missing = tuple(field for field in required_fields if field not in payload)
    if missing:
        return ResultValidity(
            ResultValidityStatus.UNREPRODUCIBLE,
            ("result is missing evidence fields: " + ", ".join(missing),),
        )
    if store is None:
        return ResultValidity(
            ResultValidityStatus.UNREPRODUCIBLE,
            ("immutable evidence store was not provided",),
        )

    errors: list[str] = []
    snapshot = None
    manifest_path = _resolve_manifest_path(payload["data_snapshot_manifest"], result_path)
    if manifest_path is None:
        errors.append("data snapshot manifest path is invalid")
    else:
        try:
            snapshot = store.load_snapshot(manifest_path)
        except Exception as exc:  # noqa: BLE001 - diagnostic boundary must fail closed
            errors.append(f"snapshot evidence cannot be verified: {exc}")

    if snapshot is not None:
        manifest = snapshot.manifest
        if payload["data_snapshot_id"] != manifest.snapshot_id:
            errors.append("result data snapshot identity does not match its manifest")
        if payload["data_cutoff"] != manifest.decision_time.session.isoformat():
            errors.append("result data cutoff does not match its snapshot")
        definition = manifest.definition
        if definition is None:
            errors.append("snapshot has no definition evidence")
        else:
            if payload["definition_snapshot_id"] != definition.digest:
                errors.append("result definition snapshot identity does not match its manifest")
            if payload["definition_fingerprint"] != definition.fingerprint:
                errors.append("result definition fingerprint does not match its manifest")

    expected_fingerprint = _fingerprint_value(current_definition_fingerprint)
    if expected_fingerprint is None:
        errors.append("current research definition cannot be resolved")
    definition_stale = (
        expected_fingerprint is not None
        and payload["definition_fingerprint"] != expected_fingerprint
    )
    if definition_stale:
        errors.append("current research-definition fingerprint differs")

    data_stale = False
    if snapshot is not None:
        current_time = now or datetime.now(UTC)
        if current_time.tzinfo is None:
            errors.append("validity clock must be timezone-aware")
        else:
            session_calendar = calendar or PrimaryUSSessionCalendar()
            required_session = session_calendar.latest_completed_session(current_time)
            snapshot_session = snapshot.manifest.decision_time.session
            if snapshot_session < required_session:
                data_stale = True
                errors.append(
                    f"snapshot cutoff {snapshot_session} is older than required session "
                    f"{required_session}"
                )
            elif snapshot_session > required_session:
                errors.append(
                    f"snapshot cutoff {snapshot_session} is newer than required session "
                    f"{required_session}"
                )

    if errors and snapshot is None:
        status = ResultValidityStatus.UNREPRODUCIBLE
    elif any("does not match" in error or "has no definition" in error for error in errors):
        status = ResultValidityStatus.UNREPRODUCIBLE
    elif definition_stale:
        status = ResultValidityStatus.DEFINITION_STALE
    elif data_stale:
        status = ResultValidityStatus.DATA_STALE
    elif errors:
        status = ResultValidityStatus.UNREPRODUCIBLE
    else:
        status = ResultValidityStatus.VALID
    return ResultValidity(status, tuple(errors))


def _fingerprint_value(value: str | DefinitionBlobRef | None) -> str | None:
    if isinstance(value, DefinitionBlobRef):
        return value.fingerprint
    return value


def _resolve_manifest_path(value: object, result_path: Path | None) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
        return candidate
    if result_path is not None:
        relative_to_result = result_path.parent / candidate
        if relative_to_result.exists():
            return relative_to_result
    return candidate


def declares_incomplete_result(payload: Mapping[str, object]) -> bool:
    """Reject result files that explicitly identify failed or partial execution."""
    if payload.get("partial") is True or payload.get("complete") is False:
        return True
    for key in ("status", "run_status", "execution_status"):
        value = payload.get(key)
        if isinstance(value, str) and value.lower() in {"failed", "partial", "incomplete"}:
            return True
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return False
    if metadata.get("partial") is True or metadata.get("complete") is False:
        return True
    return any(
        isinstance(metadata.get(key), str)
        and metadata[key].lower() in {"failed", "partial", "incomplete"}
        for key in ("status", "run_status", "execution_status")
    )
