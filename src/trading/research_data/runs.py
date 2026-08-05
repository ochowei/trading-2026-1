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
from trading.research_data.store import ResearchDataStore


class RunMode(StrEnum):
    """Persistence and data-source policy for one research execution."""

    ONLINE = "online"
    OFFLINE = "offline"
    EPHEMERAL = "ephemeral"


class RunEvidenceError(RuntimeError):
    """A formal run lacks complete immutable data or definition evidence."""


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
    ) -> None:
        self.store = store
        self.results_root = Path(results_root)
        self.now = now or (lambda: datetime.now(UTC))
        self.calendar = calendar or PrimaryUSSessionCalendar()

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
                    "current research definition does not match snapshot evidence"
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
        produced = runner(snapshot.bundle)
        if not isinstance(produced, dict):
            raise TypeError("research runner must return a result dictionary")
        result = copy.deepcopy(produced)
        raw_metadata = result.setdefault("metadata", {})
        if not isinstance(raw_metadata, dict):
            raise TypeError("research result metadata must be an object")
        raw_metadata["reproducibility"] = {
            "snapshot_id": snapshot.manifest.snapshot_id,
            "snapshot_manifest": str(Path(manifest_path)),
            "definition_fingerprint": (
                snapshot.manifest.definition.fingerprint
                if snapshot.manifest.definition is not None
                else None
            ),
            "run_mode": run_mode.value,
        }
        if run_mode is RunMode.EPHEMERAL:
            return ResearchRunOutcome(result, run_mode, None, None)

        current_time = current_time or self.now()
        if current_time.tzinfo is None:
            raise ValueError("research run clock must be timezone-aware")
        directory = self.results_root / experiment_name
        directory.mkdir(parents=True, exist_ok=True)
        stamp = current_time.astimezone(UTC).strftime("%Y%m%d_%H%M%S_%f")
        historical = directory / f"{stamp}_{run_mode.value}_{uuid.uuid4().hex}.json"
        content = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
        _atomic_write(historical, content)
        if run_mode is RunMode.OFFLINE:
            return ResearchRunOutcome(result, run_mode, historical, None)

        latest = directory / "latest.json"
        _atomic_write(latest, content)
        return ResearchRunOutcome(result, run_mode, historical, latest)


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
