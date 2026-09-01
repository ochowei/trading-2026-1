"""Versioned persisted-result schema and read-only validity classification."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from pathlib import Path

from trading.core.accounting import parse_timestamp
from trading.core.qualification import (
    HISTORICAL_QUALIFICATION_GATE_NAMES,
    SHADOW_ACTIVATION_GATE_NAMES,
    HistoricalScreenThresholds,
    validate_historical_thresholds,
)
from trading.core.sleeve_engine import (
    CANONICAL_SLEEVE_ENGINE_VERSION,
    compute_daily_equity_metrics,
)
from trading.market_data import PrimaryUSSessionCalendar, SessionCalendar
from trading.research_data.definitions import ResearchDefinitionStore
from trading.research_data.models import DefinitionBlobRef, SnapshotManifest
from trading.research_data.paths import ResultPathMigrationError, resolve_result_path
from trading.research_data.store import ResearchDataStore

CURRENT_RESULT_SCHEMA_VERSION = 3


class ResultValidityStatus(StrEnum):
    """The decision-grade status of one persisted research result."""

    VALID = "valid"
    DATA_STALE = "data-stale"
    DEFINITION_STALE = "definition-stale"
    UNREPRODUCIBLE = "unreproducible"
    LEGACY = "legacy"
    MIGRATION_PENDING = "migration-pending"


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
    """Attach the current schema and immutable evidence to one runner output."""
    if manifest.definition is None:
        raise ResultSchemaError("persisted result requires a research-definition snapshot")

    payload = copy.deepcopy(dict(produced))
    canonical_error = _canonical_sleeve_evidence_error(payload.get("canonical_sleeve_evidence"))
    if canonical_error is not None:
        raise ResultSchemaError(canonical_error)
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
            "validity": {
                "status": (
                    ResultValidityStatus.MIGRATION_PENDING.value
                    if run_mode == "migration"
                    else ResultValidityStatus.VALID.value
                ),
                "reasons": [],
            },
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
    qualification_error = _qualification_evidence_error(payload)
    if qualification_error is not None:
        raise ResultSchemaError(qualification_error)
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
    requested_path = Path(path)
    try:
        result_path = resolve_result_path(requested_path)
        loaded = json.loads(result_path.read_text(encoding="utf-8"))
    except ResultPathMigrationError as exc:
        raise ResultSchemaError(f"cannot read result {requested_path}: {exc}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultSchemaError(f"cannot read result {requested_path}: {exc}") from exc
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
    if schema_version == 2:
        return ResultValidity(
            ResultValidityStatus.LEGACY,
            ("result predates canonical sleeve evidence",),
        )
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
        "canonical_sleeve_evidence",
        "run_mode",
    )
    missing = tuple(field for field in required_fields if field not in payload)
    if missing:
        return ResultValidity(
            ResultValidityStatus.UNREPRODUCIBLE,
            ("result is missing evidence fields: " + ", ".join(missing),),
        )
    canonical_error = _canonical_sleeve_evidence_error(payload.get("canonical_sleeve_evidence"))
    if canonical_error is not None:
        return ResultValidity(ResultValidityStatus.UNREPRODUCIBLE, (canonical_error,))
    qualification_error = _qualification_evidence_error(payload)
    if qualification_error is not None:
        return ResultValidity(ResultValidityStatus.UNREPRODUCIBLE, (qualification_error,))
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
            try:
                definition_payload = ResearchDefinitionStore(store.root).load(definition)
                validate_canonical_evidence_against_definition(
                    payload.get("canonical_sleeve_evidence"),
                    definition_payload,
                )
            except Exception as exc:  # noqa: BLE001 - validity must fail closed
                errors.append(f"canonical sleeve evidence cannot be verified: {exc}")

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
    migration_pending = payload.get("run_mode") == "migration"
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
    elif migration_pending:
        status = ResultValidityStatus.MIGRATION_PENDING
    elif errors:
        status = ResultValidityStatus.UNREPRODUCIBLE
    else:
        status = ResultValidityStatus.VALID
    return ResultValidity(status, tuple(errors))


def _canonical_sleeve_evidence_error(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return "result requires canonical sleeve evidence"
    required = {
        "engine_version",
        "ranking_scenario",
        "initial_capital",
        "cost_policies",
        "raw_signals",
        "raw_candidates",
        "scenarios",
        "parity",
    }
    missing = sorted(required.difference(value))
    if missing:
        return "canonical sleeve evidence is missing fields: " + ", ".join(missing)
    if value.get("engine_version") != CANONICAL_SLEEVE_ENGINE_VERSION:
        return "canonical sleeve evidence has an unsupported engine version"
    if value.get("ranking_scenario") != "base_net":
        return "canonical sleeve evidence must rank the base_net scenario"
    policies = value.get("cost_policies")
    if not isinstance(policies, Mapping) or not {"base", "stress"}.issubset(policies):
        return "canonical sleeve evidence requires base and stress cost policies"
    scenarios = value.get("scenarios")
    if not isinstance(scenarios, Mapping):
        return "canonical sleeve evidence scenarios must be an object"
    for name in ("gross", "base_net", "stress_net"):
        scenario = scenarios.get(name)
        if not isinstance(scenario, Mapping):
            return f"canonical sleeve evidence requires {name} scenario"
        if not {"metrics", "trades", "daily_equity"}.issubset(scenario):
            return f"canonical sleeve evidence {name} scenario is incomplete"
        metric_error = _scenario_metric_error(
            scenario,
            initial_capital=value.get("initial_capital"),
        )
        if metric_error is not None:
            return f"canonical sleeve evidence {name} {metric_error}"
    if not isinstance(value.get("raw_signals"), list):
        return "canonical sleeve raw signals must be a list"
    if not isinstance(value.get("raw_candidates"), list):
        return "canonical sleeve raw candidates must be a list"
    parity = value.get("parity")
    if not isinstance(parity, Mapping):
        return "canonical sleeve parity must be an object"
    parity_fields = {
        "signal_differences",
        "trade_differences",
        "trade_comparisons",
        "has_unclassified_differences",
    }
    if not parity_fields.issubset(parity):
        return "canonical sleeve parity is incomplete"
    return None


def _qualification_evidence_error(payload: Mapping[str, object]) -> str | None:
    development = payload.get("development_summary", {})
    folds = payload.get("historical_stability_folds", [])
    shadow = payload.get("shadow_evidence", {})
    live = payload.get("live_evidence", {})
    if not isinstance(development, Mapping):
        return "development summary must be an object"
    if not isinstance(folds, list):
        return "historical stability folds must be a list"
    if not isinstance(shadow, Mapping):
        return "shadow evidence must be an object"
    if not isinstance(live, Mapping):
        return "live evidence must be an object"
    if live:
        return "Phase 6 qualification results cannot contain live evidence"

    screen = development.get("historical_screen")
    if isinstance(screen, Mapping) and screen.get("disposition") == "active":
        return "historical qualification cannot grant Active status"
    if folds:
        plan = development.get("historical_plan")
        if not isinstance(plan, Mapping) or not isinstance(screen, Mapping):
            return "historical stability evidence requires its frozen plan and screen"
        if len(folds) < 5:
            return "historical qualification requires at least five folds"
        required_plan_fields = {
            "plan_id",
            "definition_fingerprint",
            "created_at",
            "development_years",
            "evaluation_sessions",
            "folds",
            "maximum_holding_sessions",
            "execution_lag_sessions",
            "dependency_sessions",
            "embargo_sessions",
            "thresholds",
            "benchmarks",
            "selection_adjustment",
            "cost_policies",
            "stress_drawdown_limit",
        }
        if not required_plan_fields.issubset(plan):
            return "historical qualification plan is incomplete"
        thresholds = plan.get("thresholds")
        plan_benchmarks = plan.get("benchmarks")
        selection_policy = plan.get("selection_adjustment")
        evaluation_sessions = plan.get("evaluation_sessions")
        if (
            not isinstance(thresholds, Mapping)
            or not {
                "minimum_development_years",
                "minimum_evaluation_folds",
                "minimum_completed_trades",
                "minimum_traded_folds",
                "minimum_positive_fold_rate",
                "minimum_cumulative_return",
                "minimum_profit_factor",
                "minimum_stress_cumulative_return",
                "minimum_stress_profit_factor",
                "maximum_fold_concentration",
                "selection_confidence",
            }.issubset(thresholds)
            or not isinstance(plan_benchmarks, Mapping)
            or not {"family_baseline_trial_id", "random_seed", "random_samples"}.issubset(
                plan_benchmarks
            )
            or not isinstance(selection_policy, Mapping)
            or not {"repetitions", "block_sessions"}.issubset(selection_policy)
            or not isinstance(evaluation_sessions, list)
            or not evaluation_sessions
        ):
            return "historical qualification plan policy is incomplete"
        try:
            validate_historical_thresholds(
                HistoricalScreenThresholds(
                    minimum_development_years=int(thresholds["minimum_development_years"]),
                    minimum_evaluation_folds=int(thresholds["minimum_evaluation_folds"]),
                    minimum_completed_trades=int(thresholds["minimum_completed_trades"]),
                    minimum_traded_folds=int(thresholds["minimum_traded_folds"]),
                    minimum_positive_fold_rate=Decimal(
                        str(thresholds["minimum_positive_fold_rate"])
                    ),
                    minimum_cumulative_return=Decimal(str(thresholds["minimum_cumulative_return"])),
                    minimum_profit_factor=Decimal(str(thresholds["minimum_profit_factor"])),
                    minimum_stress_cumulative_return=Decimal(
                        str(thresholds["minimum_stress_cumulative_return"])
                    ),
                    minimum_stress_profit_factor=Decimal(
                        str(thresholds["minimum_stress_profit_factor"])
                    ),
                    maximum_fold_concentration=Decimal(
                        str(thresholds["maximum_fold_concentration"])
                    ),
                    selection_confidence=Decimal(str(thresholds["selection_confidence"])),
                )
            )
        except (TypeError, ValueError, InvalidOperation) as exc:
            return f"historical qualification thresholds are invalid: {exc}"
        development_years = plan.get("development_years")
        try:
            created_at = parse_timestamp(str(plan.get("created_at")))
            maximum_holding = int(plan.get("maximum_holding_sessions"))
            execution_lag = int(plan.get("execution_lag_sessions"))
            dependency_sessions = int(plan.get("dependency_sessions"))
            embargo_sessions = int(plan.get("embargo_sessions"))
        except (TypeError, ValueError):
            return "historical qualification dependencies are invalid"
        if (
            not isinstance(development_years, list)
            or len(development_years) < 3
            or not all(isinstance(year, int) for year in development_years)
            or development_years != list(range(development_years[0], development_years[-1] + 1))
            or min(maximum_holding, execution_lag, dependency_sessions, embargo_sessions) < 0
            or dependency_sessions < maximum_holding + execution_lag
            or embargo_sessions < execution_lag
        ):
            return "historical qualification dependencies are incomplete"
        try:
            parsed_evaluation_sessions = tuple(
                date.fromisoformat(str(item)) for item in evaluation_sessions
            )
        except ValueError:
            return "historical qualification evaluation sessions are invalid"
        if parsed_evaluation_sessions != tuple(sorted(set(parsed_evaluation_sessions))):
            return "historical qualification evaluation sessions are invalid"
        expected_legacy_years = list(
            range(
                parsed_evaluation_sessions[0].year - int(thresholds["minimum_development_years"]),
                parsed_evaluation_sessions[0].year,
            )
        )
        role_calendar = plan.get("role_calendar")
        legacy_chronology = (
            set(expected_legacy_years).issubset(development_years)
            and max(development_years) < parsed_evaluation_sessions[0].year
        )
        if role_calendar is None and not legacy_chronology:
            return "nonstandard Development chronology requires an explicit role calendar"
        if role_calendar is not None:
            if not isinstance(role_calendar, Mapping) or not {
                "development_sessions",
                "warmup_sessions",
                "evaluation_sessions",
            }.issubset(role_calendar):
                return "qualification role calendar is incomplete"
            raw_development_sessions = role_calendar.get("development_sessions")
            raw_warmup_sessions = role_calendar.get("warmup_sessions")
            raw_role_evaluation_sessions = role_calendar.get("evaluation_sessions")
            raw_quarantined_sessions = role_calendar.get("quarantined_sessions", [])
            if not all(
                isinstance(items, list) and items
                for items in (
                    raw_development_sessions,
                    raw_warmup_sessions,
                    raw_role_evaluation_sessions,
                )
            ):
                return "qualification role calendar is incomplete"
            if not isinstance(raw_quarantined_sessions, list):
                return "qualification role calendar is incomplete"
            try:
                role_development = tuple(
                    date.fromisoformat(str(item)) for item in raw_development_sessions
                )
                role_warmup = tuple(date.fromisoformat(str(item)) for item in raw_warmup_sessions)
                role_evaluation = tuple(
                    date.fromisoformat(str(item)) for item in raw_role_evaluation_sessions
                )
                role_quarantined = tuple(
                    date.fromisoformat(str(item)) for item in raw_quarantined_sessions
                )
            except ValueError:
                return "qualification role calendar sessions are invalid"
            if (
                role_development != tuple(sorted(set(role_development)))
                or role_warmup != tuple(sorted(set(role_warmup)))
                or role_evaluation != parsed_evaluation_sessions
                or role_quarantined != tuple(sorted(set(role_quarantined)))
                or sorted({session.year for session in role_development}) != development_years
                or set(role_development) & set(role_warmup)
                or set(role_development) & set(role_evaluation)
                or set(role_warmup) & set(role_evaluation)
                or set(role_quarantined) & set(role_development)
                or set(role_quarantined) & set(role_warmup)
                or set(role_quarantined) & set(role_evaluation)
                or role_warmup[-1] >= role_evaluation[0]
                or len(role_warmup) < dependency_sessions
                or role_development[-1] >= created_at.date()
            ):
                return "qualification role calendar is inconsistent"
        required_fold_fields = {
            "fold_id",
            "evaluation_year",
            "signal_count",
            "candidate_count",
            "completed_trades",
            "cumulative_return",
            "stress_cumulative_return",
            "stress_max_drawdown",
            "gross_profit",
            "gross_loss",
            "stress_gross_profit",
            "stress_gross_loss",
        }
        for fold in folds:
            if not isinstance(fold, Mapping) or not required_fold_fields.issubset(fold):
                return "historical stability fold evidence is incomplete"
            if any(
                not _finite_metric(fold.get(name))
                for name in required_fold_fields - {"fold_id", "evaluation_year"}
            ):
                return "historical stability fold metrics must be finite"
        plan_folds = plan.get("folds")
        if not isinstance(plan_folds, list):
            return "historical qualification plan folds are missing"
        planned_ids = tuple(item.get("fold_id") for item in plan_folds if isinstance(item, Mapping))
        evidence_ids = tuple(fold.get("fold_id") for fold in folds)
        if len(planned_ids) != len(plan_folds) or evidence_ids != planned_ids:
            return "historical stability folds differ from the frozen qualification plan"
        try:
            first_outcome = date.fromisoformat(str(plan_folds[0].get("outcome_start")))
            last_outcome = date.fromisoformat(str(plan_folds[-1].get("outcome_end")))
        except (AttributeError, ValueError):
            return "historical qualification fold dates are invalid"
        evidence_role = plan.get("evidence_role", "historical")
        retrospective_roles = {
            "retrospective-confirmatory",
            "study-time-retrospective",
            "fixed-calendar-retrospective",
        }
        if evidence_role not in {"historical", *retrospective_roles}:
            return "qualification plan evidence role is invalid"
        evidence_audit = plan.get("evidence_audit")
        if evidence_audit is not None:
            if not isinstance(evidence_audit, Mapping) or not {
                "classification",
                "frozen_at",
                "justification",
                "trial_history_complete",
            }.issubset(evidence_audit):
                return "clean-evidence audit is incomplete"
            try:
                audit_frozen_at = parse_timestamp(str(evidence_audit.get("frozen_at")))
            except ValueError:
                return "clean-evidence audit timestamp is invalid"
            if (
                audit_frozen_at != created_at
                or evidence_audit.get("classification")
                not in {"verified-clean", "known-contaminated", "provenance-unknown"}
                or not isinstance(evidence_audit.get("justification"), str)
                or not str(evidence_audit.get("justification")).strip()
                or type(evidence_audit.get("trial_history_complete")) is not bool
            ):
                return "clean-evidence audit is inconsistent"
        if evidence_role in retrospective_roles and evidence_audit is None:
            return "retrospective qualification requires a clean-evidence audit"
        if (
            evidence_role == "historical"
            and isinstance(evidence_audit, Mapping)
            and (
                evidence_audit.get("classification") != "verified-clean"
                or evidence_audit.get("trial_history_complete") is not True
            )
        ):
            return "Historical Evaluation requires verified-clean complete provenance"
        if (
            evidence_role in {"study-time-retrospective", "fixed-calendar-retrospective"}
            and isinstance(evidence_audit, Mapping)
            and evidence_audit.get("classification") == "verified-clean"
        ):
            return "study-time retrospective evaluation cannot claim verified-clean provenance"
        if evidence_role == "historical" and created_at.date() >= first_outcome:
            return "historical qualification plan was not frozen before outcomes"
        if evidence_role in retrospective_roles and created_at.date() <= last_outcome:
            return "retrospective qualification folds were not complete at plan freeze"
        if (
            evidence_role in {"study-time-retrospective", "fixed-calendar-retrospective"}
            and role_calendar is not None
            and role_development[-1] >= role_evaluation[0]
        ):
            return "study-time retrospective Development must precede evaluation"
        if (
            evidence_role == "historical"
            and role_calendar is not None
            and role_quarantined
            and (
                role_development[-1] >= role_quarantined[0]
                or role_quarantined[-1] >= role_evaluation[0]
            )
        ):
            return "clean Historical quarantine chronology is invalid"
        forward_epoch = plan.get("forward_selection_epoch")
        if forward_epoch is not None:
            if not isinstance(forward_epoch, Mapping) or not {
                "started_at",
                "selected_trial_id",
                "included_trial_ids",
                "prior_selection_history_incomplete",
            }.issubset(forward_epoch):
                return "forward selection epoch is incomplete"
            included_trial_ids = forward_epoch.get("included_trial_ids")
            selected_trial_id = forward_epoch.get("selected_trial_id")
            family_baseline_trial_id = plan_benchmarks.get("family_baseline_trial_id")
            try:
                epoch_started_at = parse_timestamp(str(forward_epoch.get("started_at")))
            except ValueError:
                return "forward selection epoch timestamp is invalid"
            if (
                epoch_started_at != created_at
                or not isinstance(included_trial_ids, list)
                or not included_trial_ids
                or not all(isinstance(item, str) and item for item in included_trial_ids)
                or included_trial_ids != sorted(set(included_trial_ids))
                or not isinstance(selected_trial_id, str)
                or selected_trial_id not in included_trial_ids
                or family_baseline_trial_id not in included_trial_ids
                or selected_trial_id == family_baseline_trial_id
                or type(forward_epoch.get("prior_selection_history_incomplete")) is not bool
            ):
                return "forward selection epoch is inconsistent"
        retrospective_checkpoint = plan.get("retrospective_selection_checkpoint")
        if retrospective_checkpoint is not None:
            if not isinstance(retrospective_checkpoint, Mapping) or not {
                "frozen_at",
                "selected_trial_id",
                "included_trial_ids",
                "prior_selection_history_incomplete",
            }.issubset(retrospective_checkpoint):
                return "retrospective selection checkpoint is incomplete"
            retrospective_ids = retrospective_checkpoint.get("included_trial_ids")
            retrospective_selected = retrospective_checkpoint.get("selected_trial_id")
            try:
                retrospective_frozen_at = parse_timestamp(
                    str(retrospective_checkpoint.get("frozen_at"))
                )
            except ValueError:
                return "retrospective selection checkpoint timestamp is invalid"
            if (
                retrospective_frozen_at != created_at
                or not isinstance(retrospective_ids, list)
                or not retrospective_ids
                or retrospective_ids != sorted(set(retrospective_ids))
                or retrospective_selected not in retrospective_ids
                or plan_benchmarks.get("family_baseline_trial_id") not in retrospective_ids
                or retrospective_selected == plan_benchmarks.get("family_baseline_trial_id")
                or type(retrospective_checkpoint.get("prior_selection_history_incomplete"))
                is not bool
            ):
                return "retrospective selection checkpoint is inconsistent"
        if forward_epoch is not None and retrospective_checkpoint is not None:
            return "qualification plan contains conflicting selection boundaries"
        if evidence_role in retrospective_roles and retrospective_checkpoint is None:
            return "retrospective qualification requires a frozen trial universe"
        if evidence_role in retrospective_roles and forward_epoch is not None:
            return "retrospective qualification cannot claim a Forward Selection Epoch"
        if evidence_role == "historical" and retrospective_checkpoint is not None:
            return "Historical Evaluation cannot use a retrospective checkpoint"
        plan_cost_error = _cost_policies_error(plan.get("cost_policies"))
        if plan_cost_error is not None:
            return plan_cost_error
        required_screen_fields = {
            "plan_id",
            "aggregate",
            "benchmarks",
            "selection_adjustment",
            "gates",
            "passed",
            "disposition",
        }
        if not required_screen_fields.issubset(screen):
            return "historical screen evidence is incomplete"
        screen_gates = screen.get("gates")
        if (
            not isinstance(screen_gates, list)
            or tuple(gate.get("name") for gate in screen_gates if isinstance(gate, Mapping))
            != HISTORICAL_QUALIFICATION_GATE_NAMES
        ):
            return "historical screen gates are incomplete"
        if any(not isinstance(gate, Mapping) for gate in screen_gates):
            return "historical screen gates are malformed"
        gates_passed = all(gate.get("passed") is True for gate in screen_gates)
        if screen.get("passed") is not gates_passed:
            return "historical screen pass state conflicts with its gates"
        expected_disposition = (
            "retrospectively-supported"
            if evidence_role in retrospective_roles and gates_passed
            else "retrospective-screen-failed"
            if evidence_role in retrospective_roles
            else "shadow-eligible"
            if gates_passed
            else "historical-screen-failed"
        )
        if screen.get("disposition") != expected_disposition:
            return "historical screen disposition conflicts with its gates"
        aggregate = screen.get("aggregate")
        benchmarks = screen.get("benchmarks")
        selection = screen.get("selection_adjustment")
        aggregate_fields = {
            "completed_trades",
            "traded_folds",
            "positive_traded_fold_rate",
            "cumulative_return",
            "profit_factor",
            "stress_cumulative_return",
            "stress_profit_factor",
            "stress_max_drawdown",
            "trade_fold_concentration",
            "profit_fold_concentration",
        }
        if (
            not isinstance(aggregate, Mapping)
            or not aggregate_fields.issubset(aggregate)
            or not isinstance(benchmarks, Mapping)
            or not isinstance(selection, Mapping)
            or not {"cash_return", "family_baseline_return", "random_entry_samples"}.issubset(
                benchmarks
            )
            or not {
                "selected_trial_id",
                "included_trial_ids",
                "observed_mean_excess_return",
                "adjusted_confidence",
                "repetitions",
                "block_sessions",
                "passed",
            }.issubset(selection)
        ):
            return "historical screen benchmark or selection evidence is incomplete"
        if isinstance(forward_epoch, Mapping) and (
            selection.get("selected_trial_id") != forward_epoch.get("selected_trial_id")
            or selection.get("included_trial_ids") != forward_epoch.get("included_trial_ids")
        ):
            return "historical screen differs from the forward selection epoch"
        if isinstance(retrospective_checkpoint, Mapping) and (
            selection.get("selected_trial_id") != retrospective_checkpoint.get("selected_trial_id")
            or selection.get("included_trial_ids")
            != retrospective_checkpoint.get("included_trial_ids")
        ):
            return "retrospective screen differs from its frozen trial universe"
        if any(
            not _finite_metric(aggregate.get(name))
            for name in aggregate_fields - {"profit_factor", "stress_profit_factor"}
        ) or any(
            not _finite_or_infinite_factor(aggregate.get(name))
            for name in ("profit_factor", "stress_profit_factor")
        ):
            return "historical screen aggregate metrics are invalid"
        historical_truth_error = _historical_screen_truth_error(
            plan=plan,
            screen=screen,
            folds=folds,
        )
        if historical_truth_error is not None:
            return historical_truth_error

    if shadow:
        registration = shadow.get("registration")
        evidence = shadow.get("evidence")
        activation = shadow.get("activation")
        if not all(isinstance(item, Mapping) for item in (registration, evidence, activation)):
            return "shadow evidence requires registration, evidence, and activation objects"
        if activation and activation.get("authorized_for_live_orders") is not False:
            return "Phase 6 Shadow evidence cannot authorize live orders"
        if registration.get("status") != "shadow":
            return "qualification result requires a Shadow registration"
        required_registration_fields = {
            "shadow_id",
            "trial_id",
            "historical_plan_id",
            "definition_fingerprint",
            "definition_snapshot_id",
            "definition_snapshot_byte_count",
            "prospective_start",
            "recorded_at",
            "activation_checkpoint",
            "status",
            "cost_policies",
            "activation_policy",
        }
        if not required_registration_fields.issubset(registration):
            return "Shadow registration evidence is incomplete"
        if (
            not isinstance(registration.get("definition_snapshot_id"), str)
            or not isinstance(registration.get("definition_snapshot_byte_count"), int)
            or registration.get("definition_snapshot_byte_count", 0) <= 0
        ):
            return "Shadow definition snapshot identity is invalid"
        registration_cost_error = _cost_policies_error(registration.get("cost_policies"))
        if registration_cost_error is not None:
            return registration_cost_error
        activation_policy = registration.get("activation_policy")
        if not isinstance(activation_policy, Mapping) or not {
            "minimum_completed_sessions",
            "minimum_completed_trades",
            "minimum_cumulative_return",
            "minimum_profit_factor",
            "minimum_stress_cumulative_return",
            "minimum_stress_profit_factor",
            "stress_drawdown_limit",
        }.issubset(activation_policy):
            return "Shadow activation policy is incomplete"
        try:
            prospective_time = parse_timestamp(str(registration.get("prospective_start")))
            recorded_time = parse_timestamp(str(registration.get("recorded_at")))
            activation_checkpoint = date.fromisoformat(
                str(registration.get("activation_checkpoint"))
            )
        except ValueError:
            return "Shadow registration dates are invalid"
        if recorded_time != prospective_time:
            return "Shadow prospective start does not match formal registration time"
        if activation_checkpoint <= prospective_time.date():
            return "Shadow activation checkpoint is not prospective"
        plan = development.get("historical_plan")
        screen = development.get("historical_screen")
        if not folds or not isinstance(plan, Mapping) or not isinstance(screen, Mapping):
            return "Shadow registration requires passing historical qualification evidence"
        if (
            plan.get("evidence_role", "historical") != "historical"
            or screen.get("passed") is not True
            or screen.get("disposition") != "shadow-eligible"
        ):
            return "Shadow registration requires a passing historical screen"
        screen_gates = screen.get("gates")
        if (
            not isinstance(screen_gates, list)
            or not screen_gates
            or any(
                not isinstance(gate, Mapping) or gate.get("passed") is not True
                for gate in screen_gates
            )
        ):
            return "Shadow registration requires all historical gates to pass"
        plan_id = plan.get("plan_id")
        selection = screen.get("selection_adjustment")
        if (
            screen.get("plan_id") != plan_id
            or registration.get("historical_plan_id") != plan_id
            or not isinstance(selection, Mapping)
            or registration.get("trial_id") != selection.get("selected_trial_id")
        ):
            return "Shadow registration does not match historical qualification lineage"
        if registration.get("cost_policies") != plan.get("cost_policies"):
            return "Shadow cost policies do not match the frozen historical plan"
        shadow_id = registration.get("shadow_id")
        if evidence and evidence.get("shadow_id") != shadow_id:
            return "shadow prospective evidence identity does not match registration"
        if activation and activation.get("shadow_id") != shadow_id:
            return "shadow activation identity does not match registration"
        definition_fingerprint = registration.get("definition_fingerprint")
        if definition_fingerprint != payload.get("definition_fingerprint"):
            return "shadow definition fingerprint does not match result"
        if evidence and evidence.get("definition_fingerprint") != definition_fingerprint:
            return "shadow evidence changed its frozen definition"
        if evidence:
            required_evidence_fields = {
                "shadow_id",
                "definition_fingerprint",
                "as_of",
                "data_cutoff",
                "completed_sessions",
                "paper_proposals",
                "simulated_fills",
                "cumulative_return",
                "profit_factor",
                "stress_cumulative_return",
                "stress_profit_factor",
                "stress_max_drawdown",
                "critical_drift",
            }
            if not required_evidence_fields.issubset(evidence):
                return "Shadow prospective evidence is incomplete"
            if any(
                not _finite_metric(evidence.get(name))
                for name in (
                    "cumulative_return",
                    "stress_cumulative_return",
                    "stress_max_drawdown",
                )
            ) or any(
                not _finite_or_infinite_factor(evidence.get(name))
                for name in ("profit_factor", "stress_profit_factor")
            ):
                return "Shadow prospective metrics are invalid"
            if (
                not isinstance(evidence.get("paper_proposals"), list)
                or not isinstance(evidence.get("simulated_fills"), list)
                or not isinstance(evidence.get("critical_drift"), bool)
            ):
                return "Shadow prospective execution evidence is malformed"
            execution_error = _shadow_execution_evidence_error(
                registration=registration,
                evidence=evidence,
            )
            if execution_error is not None:
                return execution_error
            as_of = evidence.get("as_of")
            try:
                evidence_date = date.fromisoformat(str(as_of))
                data_cutoff = date.fromisoformat(str(evidence.get("data_cutoff")))
            except ValueError:
                return "shadow prospective evidence dates are invalid"
            if evidence_date <= prospective_time.date():
                return "shadow evidence predates formal registration"
            if data_cutoff < evidence_date:
                return "shadow data cutoff predates prospective evidence"
        if activation:
            if not evidence:
                return "shadow activation requires prospective evidence"
            if activation.get("evaluated_at") != evidence.get("as_of"):
                return "shadow activation date does not match prospective evidence"
            activation_gates = activation.get("gates")
            if (
                not isinstance(activation_gates, list)
                or tuple(gate.get("name") for gate in activation_gates if isinstance(gate, Mapping))
                != SHADOW_ACTIVATION_GATE_NAMES
            ):
                return "shadow activation gates are incomplete"
            if any(not isinstance(gate, Mapping) for gate in activation_gates):
                return "shadow activation gates are malformed"
            eligible = all(gate.get("passed") is True for gate in activation_gates)
            if activation.get("eligible") is not eligible:
                return "shadow activation eligibility conflicts with its gates"
            if (activation.get("disposition") == "activation-eligible") is not eligible:
                return "shadow activation disposition conflicts with its gates"
            activation_truth_error = _activation_truth_error(
                registration=registration,
                evidence=evidence,
                activation=activation,
            )
            if activation_truth_error is not None:
                return activation_truth_error
    return None


def _historical_screen_truth_error(
    *,
    plan: Mapping[str, object],
    screen: Mapping[str, object],
    folds: list[object],
) -> str | None:
    plan_folds = plan.get("folds")
    raw_sessions = plan.get("evaluation_sessions")
    thresholds = plan.get("thresholds")
    plan_benchmarks = plan.get("benchmarks")
    selection_policy = plan.get("selection_adjustment")
    aggregate = screen.get("aggregate")
    benchmarks = screen.get("benchmarks")
    selection = screen.get("selection_adjustment")
    gates = screen.get("gates")
    if (
        not all(
            isinstance(value, Mapping)
            for value in (
                thresholds,
                plan_benchmarks,
                selection_policy,
                aggregate,
                benchmarks,
                selection,
            )
        )
        or not isinstance(plan_folds, list)
        or not isinstance(raw_sessions, list)
    ):
        return "historical qualification evidence is malformed"
    try:
        sessions = tuple(date.fromisoformat(str(value)) for value in raw_sessions)
    except ValueError:
        return "historical evaluation sessions are invalid"
    if sessions != tuple(sorted(set(sessions))):
        return "historical evaluation sessions must be unique and chronological"
    for fold in plan_folds:
        if not isinstance(fold, Mapping) or not {
            "fold_id",
            "evaluation_year",
            "outcome_start",
            "outcome_end",
            "signal_start",
            "signal_end",
        }.issubset(fold):
            return "historical qualification fold plan is incomplete"
        try:
            year = int(fold["evaluation_year"])
            annual = tuple(session for session in sessions if session.year == year)
            outcome_start = date.fromisoformat(str(fold["outcome_start"]))
            outcome_end = date.fromisoformat(str(fold["outcome_end"]))
            signal_start = date.fromisoformat(str(fold["signal_start"]))
            signal_end = date.fromisoformat(str(fold["signal_end"]))
        except (TypeError, ValueError):
            return "historical qualification fold dates are invalid"
        if (
            len(annual) < 240
            or annual[0] != outcome_start
            or annual[-1] != outcome_end
            or not outcome_start < signal_start <= signal_end < outcome_end
        ):
            return "historical qualification folds lack complete frozen sessions"
    typed_folds = [fold for fold in folds if isinstance(fold, Mapping)]
    completed = sum(int(fold["completed_trades"]) for fold in typed_folds)
    traded = sum(int(fold["completed_trades"]) > 0 for fold in typed_folds)
    positive = sum(
        int(fold["completed_trades"]) > 0 and float(fold["cumulative_return"]) > 0
        for fold in typed_folds
    )
    cumulative = _compound_result_returns(float(fold["cumulative_return"]) for fold in typed_folds)
    stress_cumulative = _compound_result_returns(
        float(fold["stress_cumulative_return"]) for fold in typed_folds
    )
    gross_profit = sum(float(fold["gross_profit"]) for fold in typed_folds)
    gross_loss = sum(float(fold["gross_loss"]) for fold in typed_folds)
    stress_profit = sum(float(fold["stress_gross_profit"]) for fold in typed_folds)
    stress_loss = sum(float(fold["stress_gross_loss"]) for fold in typed_folds)
    profit_factor = (
        math.inf
        if gross_profit and not gross_loss
        else (gross_profit / gross_loss if gross_loss else 0.0)
    )
    stress_factor = (
        math.inf
        if stress_profit and not stress_loss
        else (stress_profit / stress_loss if stress_loss else 0.0)
    )
    expected_metrics = {
        "completed_trades": completed,
        "traded_folds": traded,
        "positive_traded_fold_rate": positive / traded if traded else 0.0,
        "cumulative_return": cumulative,
        "profit_factor": profit_factor,
        "stress_cumulative_return": stress_cumulative,
        "stress_profit_factor": stress_factor,
        "stress_max_drawdown": min(
            (float(fold["stress_max_drawdown"]) for fold in typed_folds), default=0.0
        ),
        "trade_fold_concentration": (
            max((int(fold["completed_trades"]) for fold in typed_folds), default=0) / completed
            if completed
            else 0.0
        ),
        "profit_fold_concentration": (
            max((float(fold["gross_profit"]) for fold in typed_folds), default=0.0) / gross_profit
            if gross_profit
            else 0.0
        ),
    }
    if any(
        not _metric_matches(aggregate.get(name), value) for name, value in expected_metrics.items()
    ):
        return "historical screen aggregate conflicts with fold evidence"
    random_samples = benchmarks.get("random_entry_samples")
    if not isinstance(random_samples, list) or len(random_samples) != int(
        plan_benchmarks.get("random_samples", -1)
    ):
        return "historical random-entry benchmark sample count is invalid"
    if (
        not _finite_metric(benchmarks.get("cash_return"))
        or float(benchmarks.get("cash_return", math.nan)) != 0.0
        or not _finite_metric(benchmarks.get("family_baseline_return"))
    ):
        return "historical benchmark metrics are invalid"
    for sample_index, sample in enumerate(random_samples):
        if (
            not isinstance(sample, Mapping)
            or not {
                "sample_index",
                "cumulative_return",
                "completed_trades",
                "entry_months",
                "holding_sessions",
            }.issubset(sample)
            or not _finite_metric(sample.get("cumulative_return"))
        ):
            return "historical random-entry benchmark sample is malformed"
        entry_months = sample.get("entry_months")
        holding_sessions = sample.get("holding_sessions")
        if (
            sample.get("sample_index") != sample_index
            or sample.get("completed_trades") != completed
            or not isinstance(entry_months, list)
            or not isinstance(holding_sessions, list)
            or len(entry_months) != completed
            or len(holding_sessions) != completed
            or any(not isinstance(month, int) or not 1 <= month <= 12 for month in entry_months)
            or any(not isinstance(value, int) or value < 0 for value in holding_sessions)
        ):
            return "historical random-entry benchmark exposure is malformed"
    included = selection.get("included_trial_ids")
    selected = selection.get("selected_trial_id")
    baseline_id = plan_benchmarks.get("family_baseline_trial_id")
    try:
        observed_mean = Decimal(str(selection.get("observed_mean_excess_return")))
        confidence = Decimal(str(selection.get("adjusted_confidence")))
        required_confidence = Decimal(str(thresholds.get("selection_confidence")))
    except InvalidOperation:
        return "historical selection adjustment confidence is invalid"
    if (
        not observed_mean.is_finite()
        or not confidence.is_finite()
        or not isinstance(included, list)
        or not all(isinstance(item, str) for item in included)
        or len(included) != len(set(included))
        or selected not in included
        or baseline_id not in included
        or selection.get("repetitions") != selection_policy.get("repetitions")
        or selection.get("block_sessions") != selection_policy.get("block_sessions")
        or selection.get("passed") is not (confidence >= required_confidence)
    ):
        return "historical selection adjustment conflicts with frozen policy"
    random_returns = tuple(float(sample["cumulative_return"]) for sample in random_samples)
    random_threshold = sorted(random_returns)[max(0, math.ceil(0.9 * len(random_returns)) - 1)]
    expected_gates = {
        "completed_trades": completed >= int(thresholds["minimum_completed_trades"]),
        "traded_folds": traded >= int(thresholds["minimum_traded_folds"]),
        "positive_traded_folds": Decimal(str(expected_metrics["positive_traded_fold_rate"]))
        >= Decimal(str(thresholds["minimum_positive_fold_rate"])),
        "aggregate_cumulative_return": Decimal(str(cumulative))
        > Decimal(str(thresholds["minimum_cumulative_return"])),
        "aggregate_profit_factor": math.isinf(profit_factor)
        or Decimal(str(profit_factor)) > Decimal(str(thresholds["minimum_profit_factor"])),
        "stress_cumulative_return": Decimal(str(stress_cumulative))
        > Decimal(str(thresholds["minimum_stress_cumulative_return"])),
        "stress_profit_factor": math.isinf(stress_factor)
        or Decimal(str(stress_factor)) > Decimal(str(thresholds["minimum_stress_profit_factor"])),
        "stress_drawdown": Decimal(str(expected_metrics["stress_max_drawdown"]))
        >= -Decimal(str(plan.get("stress_drawdown_limit", "0"))),
        "trade_fold_concentration": Decimal(str(expected_metrics["trade_fold_concentration"]))
        <= Decimal(str(thresholds["maximum_fold_concentration"])),
        "profit_fold_concentration": Decimal(str(expected_metrics["profit_fold_concentration"]))
        <= Decimal(str(thresholds["maximum_fold_concentration"])),
        "cash_benchmark": cumulative > float(benchmarks.get("cash_return", 0)),
        "family_baseline_benchmark": cumulative
        > float(benchmarks.get("family_baseline_return", 0)),
        "random_entry_benchmark": cumulative > random_threshold,
        "selection_adjusted_confidence": selection.get("passed") is True,
    }
    gate_map = {str(gate.get("name")): gate for gate in gates if isinstance(gate, Mapping)}
    if any(gate_map[name].get("passed") is not passed for name, passed in expected_gates.items()):
        return "historical screen gates conflict with evidence"
    return None


def _compound_result_returns(values) -> float:
    equity = 1.0
    for value in values:
        equity *= 1.0 + value
    return equity - 1.0


def _metric_matches(actual: object, expected: float | int) -> bool:
    if expected == math.inf:
        return actual == "Infinity"
    try:
        return math.isclose(float(str(actual)), float(expected), rel_tol=1e-12, abs_tol=1e-12)
    except (TypeError, ValueError):
        return False


def _shadow_execution_evidence_error(
    *,
    registration: Mapping[str, object],
    evidence: Mapping[str, object],
) -> str | None:
    proposals = evidence.get("paper_proposals")
    fills = evidence.get("simulated_fills")
    if not isinstance(proposals, list) or not isinstance(fills, list):
        return "Shadow prospective execution evidence is malformed"
    try:
        start = parse_timestamp(str(registration.get("prospective_start"))).date()
        as_of = date.fromisoformat(str(evidence.get("as_of")))
        cutoff = date.fromisoformat(str(evidence.get("data_cutoff")))
    except ValueError:
        return "Shadow prospective execution dates are invalid"
    proposal_ids: list[str] = []
    for proposal in proposals:
        if not isinstance(proposal, Mapping) or not {
            "proposal_id",
            "signal_date",
            "entry_date",
            "action",
        }.issubset(proposal):
            return "Shadow paper proposal is incomplete"
        try:
            signal = date.fromisoformat(str(proposal["signal_date"]))
            entry = date.fromisoformat(str(proposal["entry_date"]))
        except ValueError:
            return "Shadow paper proposal dates are invalid"
        proposal_id = proposal.get("proposal_id")
        if (
            not isinstance(proposal_id, str)
            or not proposal_id
            or proposal.get("action") != "BUY"
            or signal <= start
            or signal > as_of
            or entry < signal
            or entry > cutoff
        ):
            return "Shadow paper proposal conflicts with prospective evidence"
        proposal_ids.append(proposal_id)
    if len(proposal_ids) != len(set(proposal_ids)):
        return "Shadow paper proposal identities are duplicated"
    fill_ids: list[str] = []
    for fill in fills:
        if not isinstance(fill, Mapping) or not {
            "proposal_id",
            "quantity",
            "executed_entry_price",
            "executed_exit_price",
            "pnl",
        }.issubset(fill):
            return "canonical simulated fill is incomplete"
        if (
            not isinstance(fill.get("proposal_id"), str)
            or any(
                not _finite_metric(fill.get(name))
                for name in (
                    "quantity",
                    "executed_entry_price",
                    "executed_exit_price",
                    "pnl",
                )
            )
            or float(fill["quantity"]) <= 0
            or float(fill["executed_entry_price"]) <= 0
            or float(fill["executed_exit_price"]) <= 0
        ):
            return "canonical simulated fill terms are invalid"
        fill_ids.append(str(fill["proposal_id"]))
    if len(fill_ids) != len(set(fill_ids)) or not set(fill_ids).issubset(proposal_ids):
        return "canonical simulated fills do not link unique paper proposals"
    return None


def _activation_truth_error(
    *,
    registration: Mapping[str, object],
    evidence: Mapping[str, object],
    activation: Mapping[str, object],
) -> str | None:
    policy = registration.get("activation_policy")
    gates = activation.get("gates")
    fills = evidence.get("simulated_fills")
    if (
        not isinstance(policy, Mapping)
        or not isinstance(gates, list)
        or not isinstance(fills, list)
    ):
        return "shadow activation source evidence is malformed"
    gate_map = {str(gate.get("name")): gate for gate in gates if isinstance(gate, Mapping)}
    try:
        expected = {
            "shadow_identity": evidence.get("shadow_id") == registration.get("shadow_id"),
            "definition_unchanged": (
                evidence.get("definition_fingerprint") == registration.get("definition_fingerprint")
                and gate_map["definition_unchanged"].get("actual")
                == registration.get("definition_fingerprint")
            ),
            "activation_checkpoint": date.fromisoformat(str(evidence.get("as_of")))
            >= date.fromisoformat(str(registration.get("activation_checkpoint"))),
            "completed_sessions": int(evidence.get("completed_sessions", -1))
            >= int(policy.get("minimum_completed_sessions", -1)),
            "completed_trades": len(fills) >= int(policy.get("minimum_completed_trades", -1)),
            "prospective_cumulative_return": Decimal(str(evidence.get("cumulative_return")))
            > Decimal(str(policy.get("minimum_cumulative_return"))),
            "prospective_profit_factor": Decimal(str(evidence.get("profit_factor")))
            > Decimal(str(policy.get("minimum_profit_factor"))),
            "stress_cumulative_return": Decimal(str(evidence.get("stress_cumulative_return")))
            > Decimal(str(policy.get("minimum_stress_cumulative_return"))),
            "stress_profit_factor": Decimal(str(evidence.get("stress_profit_factor")))
            > Decimal(str(policy.get("minimum_stress_profit_factor"))),
            "stress_drawdown": Decimal(str(evidence.get("stress_max_drawdown")))
            >= -Decimal(str(policy.get("stress_drawdown_limit"))),
            "critical_drift": evidence.get("critical_drift") is False,
        }
    except (KeyError, TypeError, ValueError, InvalidOperation):
        return "shadow activation source evidence is malformed"
    if any(gate_map[name].get("passed") is not passed for name, passed in expected.items()):
        return "shadow activation gates conflict with prospective evidence"
    return None


def _finite_metric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _finite_or_infinite_factor(value: object) -> bool:
    if value == "Infinity":
        return True
    try:
        return math.isfinite(float(str(value)))
    except (TypeError, ValueError):
        return False


def _cost_policies_error(value: object) -> str | None:
    if not isinstance(value, Mapping):
        return "qualification cost policies must be an object"
    required = {"entry_slippage_bps", "exit_slippage_bps", "fee_bps_per_side"}
    for name in ("base", "stress"):
        policy = value.get(name)
        if not isinstance(policy, Mapping) or not required.issubset(policy):
            return "qualification cost policies are incomplete"
        if any(not _finite_metric(policy.get(field)) for field in required):
            return "qualification cost policies must be finite"
    return None


def _scenario_metric_error(
    scenario: Mapping[str, object],
    *,
    initial_capital: object,
) -> str | None:
    if not isinstance(initial_capital, (int, float)) or initial_capital <= 0:
        return "has invalid initial capital"
    daily_equity = scenario.get("daily_equity")
    if not isinstance(daily_equity, list):
        return "daily equity must be a list"
    try:
        equities = [float(point["equity"]) for point in daily_equity if isinstance(point, Mapping)]
    except (KeyError, TypeError, ValueError):
        return "daily equity is invalid"
    if len(equities) != len(daily_equity):
        return "daily equity is invalid"
    computed = asdict(
        compute_daily_equity_metrics(
            equities,
            initial_equity=float(initial_capital),
        )
    )
    metrics = scenario.get("metrics")
    if not isinstance(metrics, Mapping):
        return "metrics must be an object"
    for key, expected in computed.items():
        actual = metrics.get(key)
        if expected is None:
            if actual is not None:
                return "metrics do not match daily equity"
        elif not isinstance(actual, (int, float)) or not math.isclose(
            float(actual),
            float(expected),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            return "metrics do not match daily equity"
    return None


def validate_canonical_evidence_against_definition(
    evidence: object,
    definition: Mapping[str, object],
) -> None:
    """Require result engine and cost assumptions to match frozen definition evidence."""
    error = _canonical_sleeve_evidence_error(evidence)
    if error is not None:
        raise ResultSchemaError(error)
    if not isinstance(evidence, Mapping):  # pragma: no cover - established above
        raise ResultSchemaError("result requires canonical sleeve evidence")
    if evidence.get("engine_version") != definition.get("execution_engine_version"):
        raise ResultSchemaError(
            "canonical sleeve engine version does not match research definition"
        )
    if evidence.get("cost_policies") != definition.get("execution_cost_policies"):
        raise ResultSchemaError("canonical sleeve cost policies do not match research definition")


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
