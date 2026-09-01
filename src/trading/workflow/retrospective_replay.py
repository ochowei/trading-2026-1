"""Provider-free fixed-calendar retrospective execution replay and atomic evidence publication."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from trading.core.accounting import canonical_json_bytes
from trading.core.ledger_storage import locked_file
from trading.core.sleeve_engine import (
    CanonicalSleeveInput,
    SleeveTrade,
    evaluate_canonical_sleeve_input,
)
from trading.market_data import PrimaryUSSessionCalendar
from trading.research_data import (
    ExperimentTrialRegistry,
    QualificationRegistry,
    ResearchDataStore,
    ResearchDefinitionStore,
)
from trading.research_data.shared_qualification_state import (
    resolve_study_qualification_registry_path,
)
from trading.workflow.qualification import (
    _load_trial_input,
    _verify_formal_snapshot_observation,
    _verify_snapshot_cutoff,
)
from trading.workflow.study_qualification import (
    FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    load_frozen_study_qualification_spec,
)
from trading.workflow.terminal_evidence import _validate_challenge_manifest

REPLAY_STAGE = "retrospective-execution-replay"
REPLAY_SCHEMA_VERSION = 1
MINIMUM_REPLAY_FILLS = 12


@dataclass(frozen=True, slots=True)
class RetrospectiveReplayPublication:
    """Deterministic paths and decision produced by one replay operation."""

    replay_id: str
    directory: Path
    replay_path: Path
    manifest_path: Path
    passed: bool
    dry_run: bool


def run_fixed_calendar_retrospective_replay(
    *,
    study_path: Path,
    plan_id: str,
    selected_manifest_path: Path,
    challenge_manifest_path: Path,
    qualification_registry_path: Path,
    trial_registry_path: Path,
    research_data_store: ResearchDataStore,
    definition_store: ResearchDefinitionStore,
    output_root: Path | None = None,
    dry_run: bool,
) -> RetrospectiveReplayPublication:
    """Recompute the frozen 2025 selected-candidate replay without providers or authority writes."""
    study = Path(study_path).resolve()
    spec = load_frozen_study_qualification_spec(study)
    if spec.route != FIXED_CALENDAR_RETROSPECTIVE_ROUTE:
        raise ValueError("retrospective replay requires fixed-calendar-retrospective route")
    if spec.replay_start != date(2025, 1, 1) or spec.replay_end != date(2025, 12, 31):
        raise ValueError("retrospective replay dates differ from the released 2025 contract")
    if not plan_id.strip():
        raise ValueError("retrospective replay requires a qualification plan id")

    root = study.parents[4].resolve()
    expected_qualification_registry = resolve_study_qualification_registry_path(
        study,
        logical_identity=str(spec.qualification_registry_identity),
    )
    expected_trial_registry = (root / str(spec.trial_registry_identity)).resolve()
    if Path(qualification_registry_path).resolve() != expected_qualification_registry:
        raise ValueError("qualification registry path differs from frozen qualification spec")
    if Path(trial_registry_path).resolve() != expected_trial_registry:
        raise ValueError("trial registry path differs from frozen qualification spec")

    registry = QualificationRegistry(expected_qualification_registry)
    plan = registry.historical_plan(plan_id)
    if (
        plan.evidence_role != FIXED_CALENDAR_RETROSPECTIVE_ROUTE
        or plan.study_identity is None
        or plan.study_identity.study_path != spec.study_identity.study_path
    ):
        raise ValueError("qualification plan does not belong to the fixed-calendar study")
    screen = registry.historical_screen(plan_id)
    if not screen.passed or screen.disposition != "retrospectively-supported":
        raise ValueError("retrospective replay requires a passing fixed Historical Evaluation")

    challenge_path = _repo_file(root, challenge_manifest_path, "challenge manifest")
    challenge_reference = {
        "path": challenge_path.relative_to(root).as_posix(),
        "sha256": _sha256(challenge_path),
    }
    terminal_stub = {
        "study_path": spec.study_identity.study_path,
        "preregistration_sha256": spec.study_identity.preregistration_sha256,
        "qualification_spec_sha256": spec.study_identity.qualification_spec_sha256,
        "development_authorization_sha256": spec.study_identity.development_authorization_sha256,
        "candidate_freeze_sha256": spec.study_identity.candidate_freeze_sha256,
        "qualification_evidence": {"plan_id": plan_id},
        "challenge_manifest": challenge_reference,
    }
    if not _validate_challenge_manifest(study, terminal_stub):
        raise ValueError("retrospective replay requires every frozen Evaluation challenge to pass")

    selected_manifest = _repo_file(root, selected_manifest_path, "selected replay manifest")
    trial_id, family, sleeve_input, snapshot_id, data_cutoff = _load_trial_input(
        spec.research_identity,
        selected_manifest,
        research_data_store=research_data_store,
        definition_store=definition_store,
        workflow_path=spec.workflow_path,
    )
    if family != plan.experiment_family or trial_id != spec.selected_trial_id:
        raise ValueError("replay manifest does not resolve the frozen selected candidate")
    _verify_snapshot_cutoff(
        data_cutoff=data_cutoff,
        evaluation_end=spec.replay_end,
        experiment_name=spec.research_identity,
        exact=True,
    )
    _verify_formal_snapshot_observation(
        ExperimentTrialRegistry(expected_trial_registry).read(),
        trial_id=trial_id,
        snapshot_id=snapshot_id,
        minimum_observation_date=spec.replay_end,
        allowed_run_modes=frozenset({"offline"}),
    )

    expected_sessions = tuple(
        timestamp.date()
        for timestamp in PrimaryUSSessionCalendar().sessions_in_range(
            spec.replay_start,
            spec.replay_end,
        )
    )
    replay_input = _slice_replay_input(sleeve_input, expected_sessions)
    evaluation = evaluate_canonical_sleeve_input(
        replay_input,
        base_policy=spec.base_cost_policy,
        stress_policy=spec.stress_cost_policy,
    )
    payload = _replay_payload(
        study=study,
        spec=spec,
        plan_id=plan_id,
        selected_manifest=selected_manifest,
        snapshot_id=snapshot_id,
        challenge_reference=challenge_reference,
        qualification_registry_path=expected_qualification_registry,
        trial_registry_path=expected_trial_registry,
        replay_input=replay_input,
        evaluation=evaluation,
    )
    replay_bytes = canonical_json_bytes(payload)
    replay_digest = hashlib.sha256(replay_bytes).hexdigest()
    replay_id = f"replay-{replay_digest}"
    stage_root = (
        Path(output_root).resolve()
        if output_root is not None
        else root / "results" / "workflows" / study.parents[2].name / study.name / REPLAY_STAGE
    )
    target = stage_root / replay_id
    replay_path = target / "REPLAY.json"
    manifest_path = target / "MANIFEST.json"
    manifest_payload = {
        "schema_version": 1,
        "kind": "fixed-calendar-retrospective-replay-publication",
        "study_path": spec.study_identity.study_path,
        "qualification_plan_id": plan_id,
        "replay_id": replay_id,
        "replay_path": replay_path.relative_to(root).as_posix()
        if replay_path.is_relative_to(root)
        else str(replay_path),
        "replay_sha256": replay_digest,
        "passed": payload["passed"],
        "authority": "non-actionable-historical-replay-only",
    }
    manifest_bytes = canonical_json_bytes(manifest_payload)
    publication = RetrospectiveReplayPublication(
        replay_id=replay_id,
        directory=target,
        replay_path=replay_path,
        manifest_path=manifest_path,
        passed=bool(payload["passed"]),
        dry_run=dry_run,
    )
    if dry_run:
        _verify_existing_publication(target, replay_bytes, manifest_bytes, allow_missing=True)
        return publication

    stage_root.mkdir(parents=True, exist_ok=True)
    lock_path = stage_root / ".replay-publication.lock"
    with locked_file(lock_path, 10.0):
        if target.exists():
            _verify_existing_publication(target, replay_bytes, manifest_bytes, allow_missing=False)
            return publication
        temporary = Path(tempfile.mkdtemp(prefix=".replay-stage-", dir=stage_root))
        try:
            (temporary / "REPLAY.json").write_bytes(replay_bytes)
            (temporary / "MANIFEST.json").write_bytes(manifest_bytes)
            _fsync_file(temporary / "REPLAY.json")
            _fsync_file(temporary / "MANIFEST.json")
            os.rename(temporary, target)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return publication


def validate_retrospective_replay_artifact(study_path: Path, replay_path: Path) -> bool:
    """Recompute a published replay from embedded raw values, without data or definition access."""
    study = Path(study_path).resolve()
    root = study.parents[4].resolve()
    source = _repo_file(root, replay_path, "retrospective replay")
    payload = _json_object(source)
    spec = load_frozen_study_qualification_spec(study)
    expected = {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "kind": "fixed-calendar-retrospective-execution-replay",
        "study_path": spec.study_identity.study_path,
        "route": FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
        "qualification_spec_sha256": spec.study_identity.qualification_spec_sha256,
        "candidate_freeze_sha256": spec.study_identity.candidate_freeze_sha256,
        "workflow_release_sha256": spec.study_identity.workflow_release_sha256,
        "replay_start": "2025-01-01",
        "replay_end": "2025-12-31",
        "authority": "non-actionable-historical-replay-only",
    }
    if any(payload.get(field) != value for field, value in expected.items()):
        raise ValueError("retrospective replay belongs to a different frozen study")
    replay_input = _input_from_payload(payload.get("raw_replay_input"))
    expected_sessions = tuple(
        timestamp.date()
        for timestamp in PrimaryUSSessionCalendar().sessions_in_range(
            date(2025, 1, 1), date(2025, 12, 31)
        )
    )
    if tuple(pd.Timestamp(item).date() for item in replay_input.calendar) != expected_sessions:
        raise ValueError("retrospective replay does not cover every frozen 2025 session")
    evaluation = evaluate_canonical_sleeve_input(
        replay_input,
        base_policy=spec.base_cost_policy,
        stress_policy=spec.stress_cost_policy,
    )
    recomputed = _decision_payload(
        evaluation,
        expected_sessions,
        stress_drawdown_limit=float(spec.stress_drawdown_limit),
    )
    if payload.get("decision") != recomputed or payload.get("passed") is not recomputed["passed"]:
        raise ValueError("retrospective replay decision is not provider-free reproducible")
    return bool(recomputed["passed"])


def _slice_replay_input(
    source: CanonicalSleeveInput,
    expected_sessions: tuple[date, ...],
) -> CanonicalSleeveInput:
    available = tuple(pd.Timestamp(item).date() for item in source.calendar)
    if not set(expected_sessions).issubset(available):
        missing = next(item for item in expected_sessions if item not in set(available))
        raise ValueError(f"selected replay input misses frozen session {missing.isoformat()}")
    calendar = tuple(pd.Timestamp(item) for item in expected_sessions)
    prices = source.close_prices.reindex(pd.DatetimeIndex(calendar))
    if prices.isna().any():
        raise ValueError("selected replay input has missing 2025 close prices")
    start, end = expected_sessions[0], expected_sessions[-1]
    candidates = tuple(item for item in source.candidates if start <= item.signal_date <= end)
    raw_signals = tuple(item for item in source.raw_signals if start <= item <= end)
    legacy_signals = tuple(item for item in source.legacy_signals if start <= item <= end)
    legacy_candidates = tuple(
        item for item in source.legacy_candidates if start <= item.signal_date <= end
    )
    return CanonicalSleeveInput(
        calendar=calendar,
        close_prices=prices,
        candidates=candidates,
        raw_signals=raw_signals,
        legacy_signals=legacy_signals,
        legacy_candidates=legacy_candidates,
        initial_capital=source.initial_capital,
    )


def _replay_payload(
    *,
    study: Path,
    spec: Any,
    plan_id: str,
    selected_manifest: Path,
    snapshot_id: str,
    challenge_reference: dict[str, str],
    qualification_registry_path: Path,
    trial_registry_path: Path,
    replay_input: CanonicalSleeveInput,
    evaluation: Any,
) -> dict[str, Any]:
    root = study.parents[4].resolve()
    decision = _decision_payload(
        evaluation,
        tuple(pd.Timestamp(item).date() for item in replay_input.calendar),
        stress_drawdown_limit=float(spec.stress_drawdown_limit),
    )
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "kind": "fixed-calendar-retrospective-execution-replay",
        "study_path": spec.study_identity.study_path,
        "route": FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
        "qualification_plan_id": plan_id,
        "qualification_spec_sha256": spec.study_identity.qualification_spec_sha256,
        "preregistration_sha256": spec.study_identity.preregistration_sha256,
        "development_authorization_sha256": spec.study_identity.development_authorization_sha256,
        "candidate_freeze_sha256": spec.study_identity.candidate_freeze_sha256,
        "workflow_release_sha256": spec.study_identity.workflow_release_sha256,
        "policy_set_identity": spec.policy_set_identity,
        "selected_research_identity": spec.research_identity,
        "selected_trial_id": spec.selected_trial_id,
        "selected_manifest": {
            "path": selected_manifest.relative_to(root).as_posix(),
            "sha256": _sha256(selected_manifest),
            "snapshot_id": snapshot_id,
        },
        "challenge_manifest": challenge_reference,
        "qualification_registry": {
            "path": str(spec.qualification_registry_identity),
            "sha256": _sha256(qualification_registry_path),
        },
        "trial_registry": {
            "path": trial_registry_path.relative_to(root).as_posix(),
            "sha256": _sha256(trial_registry_path),
        },
        "replay_start": spec.replay_start.isoformat(),
        "replay_end": spec.replay_end.isoformat(),
        "raw_replay_input": _input_payload(replay_input),
        "decision": decision,
        "passed": decision["passed"],
        "authority": "non-actionable-historical-replay-only",
    }


def _decision_payload(
    evaluation: Any,
    sessions: tuple[date, ...],
    *,
    stress_drawdown_limit: float = 0.20,
) -> dict[str, Any]:
    base_trades = tuple(
        item for item in evaluation.scenarios.base_net.trades if item.status == "completed"
    )
    stress_trades = tuple(
        item for item in evaluation.scenarios.stress_net.trades if item.status == "completed"
    )
    base_profit_factor = _profit_factor(base_trades)
    stress_profit_factor = _profit_factor(stress_trades)
    critical_drift = evaluation.parity_report.has_unclassified_differences
    gates = [
        _gate(
            "complete_session_coverage",
            len(sessions) == len(set(sessions)),
            len(sessions),
            len(set(sessions)),
        ),
        _gate(
            "completed_simulated_fills",
            len(base_trades) >= MINIMUM_REPLAY_FILLS,
            len(base_trades),
            MINIMUM_REPLAY_FILLS,
        ),
        _gate(
            "base_cumulative_return",
            evaluation.base_net_metrics.total_return > 0,
            evaluation.base_net_metrics.total_return,
            "> 0",
        ),
        _gate(
            "base_profit_factor",
            math.isinf(base_profit_factor) or base_profit_factor > 1,
            _ratio_text(base_profit_factor),
            "> 1",
        ),
        _gate(
            "stress_cumulative_return",
            evaluation.stress_net_metrics.total_return > 0,
            evaluation.stress_net_metrics.total_return,
            "> 0",
        ),
        _gate(
            "stress_profit_factor",
            math.isinf(stress_profit_factor) or stress_profit_factor > 1,
            _ratio_text(stress_profit_factor),
            "> 1",
        ),
        _gate(
            "stress_drawdown",
            evaluation.stress_net_metrics.max_drawdown >= -stress_drawdown_limit,
            evaluation.stress_net_metrics.max_drawdown,
            f">= -{stress_drawdown_limit}",
        ),
        _gate("historical_critical_drift", not critical_drift, critical_drift, False),
    ]
    proposals = [
        {
            "proposal_id": _proposal_id(item),
            "signal_date": item.signal_date.isoformat(),
            "entry_date": item.entry_date.isoformat(),
            "action": "BUY",
            "actionable": False,
        }
        for item in evaluation.raw_candidates
    ]
    proposal_by_terms = {
        (item["signal_date"], item["entry_date"]): item["proposal_id"] for item in proposals
    }
    fills = [
        {
            "proposal_id": proposal_by_terms[
                (item.signal_date.isoformat(), item.entry_date.isoformat())
            ],
            "quantity": item.quantity,
            "executed_entry_price": item.executed_entry_price,
            "executed_exit_price": item.executed_exit_price,
            "pnl": _trade_pnl(item),
        }
        for item in base_trades
    ]
    return {
        "completed_sessions": len(sessions),
        "non_actionable_proposals": proposals,
        "simulated_fills": fills,
        "ledger_events": [
            {"event": "paper-proposal", "proposal_id": item["proposal_id"]} for item in proposals
        ]
        + [{"event": "simulated-fill", **item} for item in fills],
        "base_metrics": asdict(evaluation.base_net_metrics),
        "stress_metrics": asdict(evaluation.stress_net_metrics),
        "base_profit_factor": _ratio_text(base_profit_factor),
        "stress_profit_factor": _ratio_text(stress_profit_factor),
        "checkpoint_prefixes": _checkpoint_prefixes(evaluation.scenarios.base_net.daily_equity),
        "critical_drift": critical_drift,
        "gates": gates,
        "passed": all(item["passed"] for item in gates),
        "insufficient_sample_is_failure": len(base_trades) < MINIMUM_REPLAY_FILLS,
    }


def _input_payload(value: CanonicalSleeveInput) -> dict[str, Any]:
    return {
        "calendar": [pd.Timestamp(item).date().isoformat() for item in value.calendar],
        "close_prices": [float(item) for item in value.close_prices],
        "candidates": [_candidate_payload(item) for item in value.candidates],
        "raw_signals": [item.isoformat() for item in value.raw_signals],
        "legacy_signals": [item.isoformat() for item in value.legacy_signals],
        "legacy_candidates": [_candidate_payload(item) for item in value.legacy_candidates],
        "initial_capital": value.initial_capital,
    }


def _input_from_payload(value: object) -> CanonicalSleeveInput:
    if not isinstance(value, dict):
        raise ValueError("retrospective replay raw input is malformed")
    try:
        calendar = tuple(pd.Timestamp(item) for item in value["calendar"])
        prices = pd.Series(value["close_prices"], index=pd.DatetimeIndex(calendar), dtype=float)
        return CanonicalSleeveInput(
            calendar=calendar,
            close_prices=prices,
            candidates=tuple(_candidate_from_payload(item) for item in value["candidates"]),
            raw_signals=tuple(date.fromisoformat(item) for item in value["raw_signals"]),
            legacy_signals=tuple(date.fromisoformat(item) for item in value["legacy_signals"]),
            legacy_candidates=tuple(
                _candidate_from_payload(item) for item in value["legacy_candidates"]
            ),
            initial_capital=float(value["initial_capital"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"retrospective replay raw input is malformed: {exc}") from exc


def _candidate_payload(value: Any) -> dict[str, Any]:
    return {
        "signal_date": value.signal_date.isoformat(),
        "entry_date": value.entry_date.isoformat(),
        "entry_price": value.entry_price,
        "exit_date": value.exit_date.isoformat() if value.exit_date else None,
        "exit_price": value.exit_price,
        "exit_type": value.exit_type,
    }


def _candidate_from_payload(value: object) -> Any:
    from trading.core.sleeve_engine import CandidateTrade

    if not isinstance(value, dict):
        raise ValueError("candidate is not an object")
    return CandidateTrade(
        signal_date=date.fromisoformat(str(value["signal_date"])),
        entry_date=date.fromisoformat(str(value["entry_date"])),
        entry_price=float(value["entry_price"]),
        exit_date=(date.fromisoformat(str(value["exit_date"])) if value.get("exit_date") else None),
        exit_price=(float(value["exit_price"]) if value.get("exit_price") is not None else None),
        exit_type=str(value["exit_type"]) if value.get("exit_type") is not None else None,
    )


def _profit_factor(trades: tuple[SleeveTrade, ...]) -> float:
    pnl = tuple(_trade_pnl(item) for item in trades)
    profit = sum(item for item in pnl if item > 0)
    loss = abs(sum(item for item in pnl if item < 0))
    return profit / loss if loss else (math.inf if profit else 0.0)


def _trade_pnl(trade: SleeveTrade) -> float:
    if trade.executed_entry_price is None or trade.executed_exit_price is None:
        raise ValueError("completed replay trade lacks executed prices")
    return (
        trade.quantity * (trade.executed_exit_price - trade.executed_entry_price) - trade.total_fees
    )


def _checkpoint_prefixes(points: tuple[Any, ...]) -> list[dict[str, Any]]:
    prefixes: list[dict[str, Any]] = []
    for index, point in enumerate(points):
        current = point.date.date()
        if index + 1 == len(points) or points[index + 1].date.month != point.date.month:
            prefixes.append(
                {
                    "through": current.isoformat(),
                    "completed_sessions": index + 1,
                    "equity": point.equity,
                    "cash": point.cash,
                    "position_value": point.position_value,
                }
            )
    return prefixes


def _proposal_id(candidate: Any) -> str:
    identity = {
        "signal_date": candidate.signal_date.isoformat(),
        "entry_date": candidate.entry_date.isoformat(),
        "entry_price": candidate.entry_price,
        "exit_date": candidate.exit_date.isoformat() if candidate.exit_date else None,
        "exit_price": candidate.exit_price,
    }
    return "paper-" + hashlib.sha256(canonical_json_bytes(identity)).hexdigest()


def _gate(name: str, passed: bool, actual: Any, threshold: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "actual": actual, "threshold": threshold}


def _ratio_text(value: float) -> str:
    return "Infinity" if math.isinf(value) else str(value)


def _repo_file(root: Path, path: Path, label: str) -> Path:
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} is outside the repository") from exc
    if not candidate.is_file():
        raise ValueError(f"{label} is missing")
    return candidate


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read retrospective replay: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("retrospective replay must be an object")
    return value


def _verify_existing_publication(
    target: Path,
    replay_bytes: bytes,
    manifest_bytes: bytes,
    *,
    allow_missing: bool,
) -> None:
    if not target.exists():
        if allow_missing:
            return
        raise ValueError("retrospective replay publication disappeared")
    if not target.is_dir() or {item.name for item in target.iterdir()} != {
        "REPLAY.json",
        "MANIFEST.json",
    }:
        raise ValueError("retrospective replay publication is partial or conflicting")
    if (target / "REPLAY.json").read_bytes() != replay_bytes or (
        target / "MANIFEST.json"
    ).read_bytes() != manifest_bytes:
        raise ValueError("retrospective replay publication collision")


def _fsync_file(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
