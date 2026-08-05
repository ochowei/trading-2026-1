"""Formal research execution modes and result publication boundaries."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from trading.market_data import (
    MarketDataBundle,
    PrimaryUSSessionCalendar,
    SessionCalendar,
)
from trading.research_data.models import DefinitionBlobRef
from trading.research_data.result_schema import (
    build_result_payload,
    declares_incomplete_result,
)
from trading.research_data.store import ResearchDataStore
from trading.research_data.trial_registry import ExperimentTrialRegistry


class RunMode(StrEnum):
    """Persistence and data-source policy for one research execution."""

    ONLINE = "online"
    OFFLINE = "offline"
    EPHEMERAL = "ephemeral"


class RunEvidenceError(RuntimeError):
    """A formal run lacks complete immutable data or definition evidence."""


class RunExecutionError(RuntimeError):
    """A runner failed or returned a result explicitly marked incomplete."""


@dataclass(frozen=True, slots=True)
class ResearchRunOutcome:
    """Result plus the exact publication effects of one execution."""

    result: dict[str, object]
    mode: RunMode
    persisted_path: Path | None
    latest_path: Path | None


class ResearchRunCoordinator:
    """Execute only against verified snapshots and enforce mode-specific writes."""

    def __init__(
        self,
        *,
        store: ResearchDataStore,
        results_root: Path,
        now: Callable[[], datetime] | None = None,
        calendar: SessionCalendar | None = None,
        trial_registry: ExperimentTrialRegistry | None = None,
        experiment_family: str | None = None,
        hypothesis: str = "",
    ) -> None:
        self.store = store
        self.results_root = Path(results_root)
        self.now = now or (lambda: datetime.now(UTC))
        self.calendar = calendar or PrimaryUSSessionCalendar()
        self.trial_registry = trial_registry or ExperimentTrialRegistry(
            self.results_root / "trial_registry.json",
            now=self.now,
        )
        self.experiment_family = experiment_family
        self.hypothesis = hypothesis

    def execute(
        self,
        experiment_name: str,
        runner: Callable[[MarketDataBundle], dict[str, object]],
        *,
        manifest_path: Path,
        current_definition: DefinitionBlobRef | None = None,
        mode: RunMode | str = RunMode.ONLINE,
    ) -> ResearchRunOutcome:
        """Verify evidence, run once, then apply the selected publication rule."""
        try:
            run_mode = RunMode(mode)
        except ValueError:
            raise ValueError("mode must be online, offline, or ephemeral") from None
        if not experiment_name or Path(experiment_name).name != experiment_name:
            raise ValueError("experiment_name must be one safe path segment")
        snapshot = self.store.load_snapshot(manifest_path)
        if run_mode is not RunMode.EPHEMERAL and snapshot.manifest.definition is None:
            raise RunEvidenceError("persisted research runs require definition evidence")
        if run_mode is not RunMode.EPHEMERAL:
            if current_definition is None:
                raise RunEvidenceError(
                    "persisted research runs require current research definition evidence"
                )
            if current_definition != snapshot.manifest.definition:
                raise RunEvidenceError(
                    "current exact research definition does not match snapshot evidence"
                )
        current_time: datetime | None = None
        if run_mode is RunMode.ONLINE:
            current_time = self.now()
            if current_time.tzinfo is None:
                raise ValueError("research run clock must be timezone-aware")
            required_session = self.calendar.latest_completed_session(current_time)
            if snapshot.manifest.decision_time.session != required_session:
                raise RunEvidenceError(
                    f"online run has stale snapshot {snapshot.manifest.decision_time.session}; "
                    f"latest completed session is {required_session}"
                )
        formal = run_mode is not RunMode.EPHEMERAL
        definition = snapshot.manifest.definition
        experiment_family = self.experiment_family
        run_id = uuid.uuid4().hex
        if formal:
            if not isinstance(experiment_family, str) or not experiment_family.strip():
                raise RunEvidenceError("formal research runs require a declared experiment family")
            if definition is None:  # pragma: no cover - checked above
                raise RunEvidenceError("persisted research runs require definition evidence")
            self.trial_registry.register_trial(
                experiment_family,
                definition.fingerprint,
                experiment_name=experiment_name,
                hypothesis=self.hypothesis,
            )

        def retain_failure(
            error: Exception,
            *,
            observation_id: str = run_id,
            result_path: Path | None = None,
        ) -> None:
            if not formal:
                return
            if definition is None or experiment_family is None:  # pragma: no cover - guarded above
                raise RunEvidenceError("formal failure lacks trial identity")
            self._record_failure(
                experiment_family=experiment_family,
                definition_fingerprint=definition.fingerprint,
                snapshot_id=snapshot.manifest.snapshot_id,
                run_mode=run_mode,
                observation_id=observation_id,
                result_path=result_path,
                error=error,
            )

        try:
            produced = runner(snapshot.bundle)
            if not isinstance(produced, dict):
                raise TypeError("research runner must return a result dictionary")
            result = copy.deepcopy(produced)
            if declares_incomplete_result(result):
                raise RunExecutionError("research runner returned a failed or partial result")
            raw_metadata = result.setdefault("metadata", {})
            if not isinstance(raw_metadata, dict):
                raise TypeError("research result metadata must be an object")
            raw_metadata["reproducibility"] = {
                "snapshot_id": snapshot.manifest.snapshot_id,
                "snapshot_manifest": str(Path(manifest_path)),
                "definition_snapshot_id": definition.digest if definition else None,
                "definition_fingerprint": definition.fingerprint if definition else None,
                "run_mode": run_mode.value,
            }
            if definition is not None:
                result = build_result_payload(
                    result,
                    manifest=snapshot.manifest,
                    manifest_path=manifest_path,
                    run_mode=run_mode.value,
                )
            elif formal:
                raise RunEvidenceError("persisted research runs require definition evidence")
        except Exception as exc:
            retain_failure(exc)
            raise

        if run_mode is RunMode.EPHEMERAL:
            return ResearchRunOutcome(result, run_mode, None, None)

        current_time = current_time or self.now()
        if current_time.tzinfo is None:
            raise ValueError("research run clock must be timezone-aware")
        directory = self.results_root / experiment_name
        directory.mkdir(parents=True, exist_ok=True)
        stamp = current_time.astimezone(UTC).strftime("%Y%m%d_%H%M%S_%f")
        historical = directory / f"{stamp}_{run_mode.value}_{uuid.uuid4().hex}.json"
        try:
            content = (
                json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            _atomic_write(historical, content)
        except Exception as exc:
            retain_failure(exc, result_path=historical)
            raise
        if formal and definition is not None and experiment_family is not None:
            self._record_success(
                experiment_family=experiment_family,
                definition_fingerprint=definition.fingerprint,
                snapshot_id=snapshot.manifest.snapshot_id,
                run_mode=run_mode,
                observation_id=run_id,
                result_path=historical,
            )
        if run_mode is RunMode.OFFLINE:
            return ResearchRunOutcome(result, run_mode, historical, None)

        latest = directory / "latest.json"
        try:
            _atomic_write(latest, content)
        except Exception as exc:
            retain_failure(
                exc,
                observation_id=f"{run_id}:latest",
                result_path=historical,
            )
            raise
        return ResearchRunOutcome(result, run_mode, historical, latest)

    def _record_success(
        self,
        *,
        experiment_family: str,
        definition_fingerprint: str,
        snapshot_id: str,
        run_mode: RunMode,
        observation_id: str,
        result_path: Path,
    ) -> None:
        self.trial_registry.record_observation(
            experiment_family,
            definition_fingerprint,
            snapshot_id=snapshot_id,
            result_path=result_path,
            run_mode=run_mode.value,
            outcome_status="succeeded",
            validity_status="valid",
            observation_id=observation_id,
        )

    def _record_failure(
        self,
        *,
        experiment_family: str,
        definition_fingerprint: str,
        snapshot_id: str,
        run_mode: RunMode,
        observation_id: str,
        result_path: Path | None = None,
        error: Exception,
    ) -> None:
        """Keep failed formal attempts while allowing ephemeral failures to disappear."""
        self.trial_registry.record_observation(
            experiment_family,
            definition_fingerprint,
            snapshot_id=snapshot_id,
            result_path=result_path,
            run_mode=run_mode.value,
            outcome_status="failed",
            failure_reason=f"{type(error).__name__}: {error}",
            observation_id=observation_id,
        )


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
