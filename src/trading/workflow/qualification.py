"""Production orchestration for forward-dated Historical qualification evidence."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from trading.core.accounting import parse_timestamp
from trading.core.qualification import (
    RETROSPECTIVE_EVIDENCE_ROLES,
    DailyExcessReturn,
    EvaluationEvidenceAudit,
    ForwardSelectionEpoch,
    HistoricalQualificationPlan,
    HistoricalScreenResult,
    RetrospectiveSelectionCheckpoint,
    StudyQualificationIdentity,
    build_historical_qualification_plan,
    evaluate_family_selection_adjustment,
    evaluate_historical_stability_screen,
)
from trading.core.qualification_transaction import publish_qualification_plan_transaction
from trading.core.sleeve_engine import (
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    CanonicalSleeveInput,
    ExecutionCostPolicy,
    evaluate_canonical_sleeve_input,
)
from trading.experiments import get_experiment
from trading.market_data import PrimaryUSSessionCalendar, SessionCalendar
from trading.research_data import (
    ExperimentTrialDeclaration,
    ExperimentTrialRegistry,
    OutcomeFreeTrialRegistration,
    QualificationRegistry,
    ResearchDataStore,
    ResearchDefinitionSnapshot,
    ResearchDefinitionStore,
)
from trading.research_data.trial_registry import formal_trial_id
from trading.research_definitions import (
    ResearchDefinitionRegistry,
    resolve_workflow_policy_set,
)


@dataclass(frozen=True, slots=True)
class QualificationScreenExecution:
    """One recomputed screen and the append-only event that records it."""

    screen: HistoricalScreenResult
    event_id: str


def register_forward_qualification_plan(
    *,
    experiment_name: str | None = None,
    research_identity: str | None = None,
    workflow_path: Path | None = None,
    family_baseline_trial_id: str,
    evaluation_years: tuple[int, ...],
    maximum_holding_sessions: int,
    execution_lag_sessions: int,
    dependency_sessions: int,
    embargo_sessions: int,
    stress_drawdown_limit: str,
    random_seed: int,
    random_samples: int,
    bootstrap_repetitions: int,
    bootstrap_block_sessions: int,
    qualification_registry_path: Path,
    trial_registry_path: Path,
    now: Callable[[], datetime] | None = None,
    calendar: SessionCalendar | None = None,
    definition_store: ResearchDefinitionStore | None = None,
    evidence_role: str = "historical",
    evidence_classification: str | None = None,
    evidence_justification: str | None = None,
    trial_history_complete: bool = False,
    development_years: tuple[int, ...] | None = None,
    warmup_start: date | None = None,
    warmup_end: date | None = None,
    quarantine_years: tuple[int, ...] | None = None,
    family_research_identities: tuple[str, ...] = (),
    dry_run: bool = False,
    family_source_sha256: Mapping[str, str] | None = None,
    maximum_family_trials: int | None = None,
    study_identity: StudyQualificationIdentity | None = None,
    base_cost_policy: ExecutionCostPolicy = DEFAULT_BASE_COST_POLICY,
    stress_cost_policy: ExecutionCostPolicy = DEFAULT_STRESS_COST_POLICY,
) -> HistoricalQualificationPlan:
    """Freeze and register one exact qualification plan without a backdated clock."""
    exact_study_required = (
        bool(family_research_identities)
        or evidence_role == "study-time-retrospective"
        or (
            evidence_role == "historical"
            and any(
                value is not None
                for value in (development_years, warmup_start, warmup_end, quarantine_years)
            )
        )
    )
    if exact_study_required and study_identity is None:
        raise ValueError("this qualification route requires an exact frozen study identity")
    temporary_definition_store: TemporaryDirectory[str] | None = None
    if dry_run and definition_store is None:
        temporary_definition_store = TemporaryDirectory(prefix="qualification-dry-run-")
        definition_store = ResearchDefinitionStore(Path(temporary_definition_store.name))
    clock = now or (lambda: datetime.now(UTC))
    started_at = clock()
    if started_at.tzinfo is None:
        raise ValueError("qualification plan clock must be timezone-aware")
    started_at = started_at.astimezone(UTC)
    years = tuple(sorted(set(evaluation_years)))
    if not years:
        raise ValueError("forward qualification plan requires evaluation years")

    strategy, policy_set = _resolve_qualification_definition(
        experiment_name=experiment_name,
        research_identity=research_identity,
        workflow_path=workflow_path,
    )
    if evidence_role in RETROSPECTIVE_EVIDENCE_ROLES:
        _require_retrospective_workflow(workflow_path, evidence_role=evidence_role)
    if research_identity is not None and evidence_classification is None:
        raise ValueError("workflow-native qualification requires a clean-evidence classification")
    audit = None
    if evidence_classification is not None:
        audit = EvaluationEvidenceAudit(
            classification=evidence_classification,
            frozen_at=started_at,
            justification=(evidence_justification or "").strip(),
            trial_history_complete=trial_history_complete,
        )
    definition = _capture_definition(strategy, definition_store, policy_set=policy_set)
    declaration = _declare_trial(strategy)
    selected_trial_id = formal_trial_id(declaration.family, definition.fingerprint)
    trial_registry = ExperimentTrialRegistry(trial_registry_path)
    registrations: tuple[OutcomeFreeTrialRegistration, ...] = ()
    expected_family_trial_ids: tuple[str, ...] | None = None
    if family_research_identities:
        if research_identity is None or workflow_path is None:
            raise ValueError("complete-family preparation requires --research and --workflow")
        identities = tuple(sorted(set(family_research_identities)))
        if len(identities) != len(family_research_identities):
            raise ValueError("complete-family preparation contains duplicate source identities")
        if research_identity not in identities:
            raise ValueError("complete-family preparation must include the selected identity")
        if maximum_family_trials != len(identities):
            raise ValueError("complete-family preparation must match the frozen trial budget")
        expected_source_hashes = dict(family_source_sha256 or {})
        if set(expected_source_hashes) != set(identities):
            raise ValueError("complete-family preparation requires every frozen source digest")
        prepared: list[OutcomeFreeTrialRegistration] = []
        expected_ids: list[str] = []
        source_registry = ResearchDefinitionRegistry()
        for identity in identities:
            source_path = source_registry.resolve(identity)
            actual_source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if expected_source_hashes[identity] != actual_source_sha:
                raise ValueError(f"complete-family source digest differs for {identity}")
            family_strategy = source_registry.load(identity)
            family_definition = _capture_definition(
                family_strategy,
                definition_store,
                policy_set=policy_set,
            )
            family_declaration = _declare_trial(family_strategy)
            if family_declaration.family != declaration.family:
                raise ValueError("complete-family preparation crosses trial families")
            trial_id = formal_trial_id(
                family_declaration.family,
                family_definition.fingerprint,
            )
            expected_ids.append(trial_id)
            prepared.append(
                OutcomeFreeTrialRegistration(
                    experiment_family=family_declaration.family,
                    definition_fingerprint=family_definition.fingerprint,
                    experiment_name=identity,
                    hypothesis=family_declaration.hypothesis,
                )
            )
        registrations = tuple(prepared)
        expected_family_trial_ids = tuple(sorted(expected_ids))
        trial_state = trial_registry.preview_registration_state(
            registrations,
            registered_at=started_at,
        )
    else:
        trial_state = trial_registry.read()
    included_trial_ids = _registered_family_trial_ids(
        trial_state,
        experiment_family=declaration.family,
        boundary_time=started_at,
    )
    if expected_family_trial_ids is not None and included_trial_ids != expected_family_trial_ids:
        raise ValueError("complete-family preparation differs from the registered family universe")
    if selected_trial_id not in included_trial_ids:
        raise ValueError("selected experiment trial is not formally registered")
    if family_baseline_trial_id not in included_trial_ids:
        raise ValueError("family baseline trial is not registered in the selected family")
    if selected_trial_id == family_baseline_trial_id:
        raise ValueError("family baseline trial must differ from the selected trial")

    session_calendar = calendar or PrimaryUSSessionCalendar()
    explicit_calendar_inputs = (
        development_years is not None,
        warmup_start is not None,
        warmup_end is not None,
    )
    if any(explicit_calendar_inputs) and not all(explicit_calendar_inputs):
        raise ValueError(
            "explicit retrospective role calendar requires development years and warmup bounds"
        )
    if any(explicit_calendar_inputs) and evidence_role == "historical" and quarantine_years is None:
        raise ValueError("explicit clean role calendar requires declared quarantine years")
    explicit_development_sessions = None
    explicit_warmup_sessions: tuple[date, ...] = ()
    explicit_quarantined_sessions: tuple[date, ...] = ()
    if all(explicit_calendar_inputs):
        assert development_years is not None
        assert warmup_start is not None
        assert warmup_end is not None
        explicit_years = tuple(sorted(set(development_years)))
        if not explicit_years:
            raise ValueError("explicit retrospective role calendar requires development years")
        if explicit_years != tuple(range(explicit_years[0], explicit_years[-1] + 1)):
            raise ValueError("explicit development years must be consecutive")
        if warmup_start > warmup_end:
            raise ValueError("warmup start must not follow warmup end")
        sessions = tuple(
            timestamp.date()
            for timestamp in session_calendar.sessions_in_range(
                date(years[0], 1, 1),
                date(years[-1], 12, 31),
            )
        )
        explicit_development_sessions = tuple(
            timestamp.date()
            for timestamp in session_calendar.sessions_in_range(
                date(explicit_years[0], 1, 1),
                date(explicit_years[-1], 12, 31),
            )
        )
        explicit_warmup_sessions = tuple(
            timestamp.date()
            for timestamp in session_calendar.sessions_in_range(warmup_start, warmup_end)
        )
        if quarantine_years is not None:
            quarantine = tuple(sorted(set(quarantine_years)))
            if quarantine and quarantine != tuple(range(quarantine[0], quarantine[-1] + 1)):
                raise ValueError("explicit quarantine years must be consecutive")
            explicit_quarantined_sessions = tuple(
                timestamp.date()
                for year in quarantine
                for timestamp in session_calendar.sessions_in_range(
                    date(year, 1, 1), date(year, 12, 31)
                )
            )
    else:
        first_development_year = years[0] - 3
        sessions = tuple(
            timestamp.date()
            for timestamp in session_calendar.sessions_in_range(
                date(first_development_year, 1, 1),
                date(years[-1], 12, 31),
            )
        )
    prior_selection_history_incomplete = (
        trial_state.get("selection_history_incomplete") is not False
    )
    epoch = None
    retrospective_checkpoint = None
    if evidence_role in RETROSPECTIVE_EVIDENCE_ROLES:
        retrospective_checkpoint = RetrospectiveSelectionCheckpoint(
            frozen_at=started_at,
            selected_trial_id=selected_trial_id,
            included_trial_ids=included_trial_ids,
            prior_selection_history_incomplete=prior_selection_history_incomplete,
        )
    else:
        epoch = ForwardSelectionEpoch(
            started_at=started_at,
            selected_trial_id=selected_trial_id,
            included_trial_ids=included_trial_ids,
            prior_selection_history_incomplete=prior_selection_history_incomplete,
        )
    plan = build_historical_qualification_plan(
        experiment_family=declaration.family,
        definition_fingerprint=definition.fingerprint,
        sessions=sessions,
        evaluation_years=years,
        maximum_holding_sessions=maximum_holding_sessions,
        execution_lag_sessions=execution_lag_sessions,
        dependency_sessions=dependency_sessions,
        embargo_sessions=embargo_sessions,
        stress_drawdown_limit=stress_drawdown_limit,
        family_baseline_trial_id=family_baseline_trial_id,
        random_seed=random_seed,
        random_samples=random_samples,
        bootstrap_repetitions=bootstrap_repetitions,
        bootstrap_block_sessions=bootstrap_block_sessions,
        created_at=started_at,
        base_cost_policy=base_cost_policy,
        stress_cost_policy=stress_cost_policy,
        forward_selection_epoch=epoch,
        retrospective_selection_checkpoint=retrospective_checkpoint,
        evidence_role=evidence_role,
        evidence_audit=audit,
        development_sessions=explicit_development_sessions,
        warmup_sessions=explicit_warmup_sessions,
        quarantined_sessions=explicit_quarantined_sessions,
        study_identity=study_identity,
    )
    if dry_run:
        if temporary_definition_store is not None:
            temporary_definition_store.cleanup()
        return plan
    qualification_registry = QualificationRegistry(
        qualification_registry_path,
        now=lambda: started_at,
    )
    qualification_registry.validate_historical_plan_registration(plan)
    if registrations:
        committed_ids = publish_qualification_plan_transaction(
            plan=plan,
            registrations=registrations,
            registered_at=started_at,
            trial_registry_path=trial_registry_path,
            qualification_registry_path=qualification_registry_path,
        )
        if tuple(sorted(committed_ids)) != expected_family_trial_ids:
            raise ValueError("atomic family registration produced an unexpected trial universe")
    else:
        qualification_registry.register_historical_plan(plan)
    return plan


def run_registered_historical_screen(
    *,
    plan_id: str,
    trial_manifests: Mapping[str, Path],
    qualification_registry_path: Path,
    trial_registry_path: Path,
    research_data_store: ResearchDataStore,
    definition_store: ResearchDefinitionStore,
    workflow_path: Path | None = None,
    now: Callable[[], datetime] | None = None,
) -> QualificationScreenExecution:
    """Recompute a frozen plan from verified formal trial snapshots and record it once."""
    clock = now or (lambda: datetime.now(UTC))
    evaluated_at = clock()
    if evaluated_at.tzinfo is None:
        raise ValueError("historical screen clock must be timezone-aware")
    evaluated_at = evaluated_at.astimezone(UTC)
    registry = QualificationRegistry(qualification_registry_path)
    plan = registry.historical_plan(plan_id)
    trial_registry_state = ExperimentTrialRegistry(trial_registry_path).read()
    allowed_observation_run_modes = (
        frozenset({"offline"})
        if plan.study_identity is not None
        and plan.study_identity.evidence_contract_sha256 is not None
        else frozenset({"offline", "online"})
    )
    exact_snapshot_cutoff = (
        plan.study_identity is not None and plan.study_identity.evidence_contract_sha256 is not None
    )

    inputs: dict[str, CanonicalSleeveInput] = {}
    for experiment_name, manifest_path in trial_manifests.items():
        trial_id, experiment_family, sleeve_input, snapshot_id, data_cutoff = _load_trial_input(
            experiment_name,
            manifest_path,
            research_data_store=research_data_store,
            definition_store=definition_store,
            workflow_path=workflow_path,
        )
        if experiment_family != plan.experiment_family:
            raise ValueError(f"{experiment_name} belongs to a different experiment family")
        if trial_id in inputs:
            raise ValueError(f"duplicate trial identity in screen inputs: {trial_id}")
        _verify_snapshot_cutoff(
            data_cutoff=data_cutoff,
            evaluation_end=plan.evaluation_sessions[-1],
            experiment_name=experiment_name,
            exact=exact_snapshot_cutoff,
        )
        _verify_formal_snapshot_observation(
            trial_registry_state,
            trial_id=trial_id,
            snapshot_id=snapshot_id,
            minimum_observation_date=plan.evaluation_sessions[-1],
            allowed_run_modes=allowed_observation_run_modes,
        )
        inputs[trial_id] = sleeve_input

    selection_boundary = plan.forward_selection_epoch or plan.retrospective_selection_checkpoint
    selected_trial_id = (
        selection_boundary.selected_trial_id
        if selection_boundary is not None
        else formal_trial_id(plan.experiment_family, plan.definition_fingerprint)
    )
    expected_trial_ids = _registered_family_trial_ids(
        trial_registry_state,
        experiment_family=plan.experiment_family,
        boundary_time=(
            plan.forward_selection_epoch.started_at
            if plan.forward_selection_epoch is not None
            else plan.retrospective_selection_checkpoint.frozen_at
            if plan.retrospective_selection_checkpoint is not None
            else None
        ),
    )
    if set(inputs) != set(expected_trial_ids):
        raise ValueError("screen inputs must cover every currently registered family trial")
    if plan.forward_selection_epoch is not None and (
        expected_trial_ids != plan.forward_selection_epoch.included_trial_ids
    ):
        raise ValueError("forward selection epoch trial universe changed after registration")
    if plan.retrospective_selection_checkpoint is not None and (
        expected_trial_ids != plan.retrospective_selection_checkpoint.included_trial_ids
    ):
        raise ValueError("retrospective trial universe changed after registration")

    returns = {
        trial_id: _daily_excess_returns(plan, sleeve_input)
        for trial_id, sleeve_input in inputs.items()
    }
    adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id=selected_trial_id,
        trial_registry_state=trial_registry_state,
        trial_daily_excess_returns=returns,
    )
    baseline_trial_id = plan.benchmarks.family_baseline_trial_id
    try:
        selected_input = inputs[selected_trial_id]
        baseline_input = inputs[baseline_trial_id]
    except KeyError as exc:
        raise ValueError(f"historical screen trial input is missing: {exc.args[0]}") from exc
    screen = evaluate_historical_stability_screen(
        plan,
        strategy_input=selected_input,
        family_baseline_trial_id=baseline_trial_id,
        family_baseline_input=baseline_input,
        family_baseline_verifier=lambda trial_id, baseline: _verify_baseline_input(
            trial_id,
            baseline,
            expected_trial_id=baseline_trial_id,
            expected_input=baseline_input,
        ),
        selection_adjustment=adjustment,
        base_policy=plan.base_cost_policy,
        stress_policy=plan.stress_cost_policy,
    )
    event_id = registry.record_historical_screen(screen, evaluated_at=evaluated_at)
    return QualificationScreenExecution(screen=screen, event_id=event_id)


def _capture_definition(
    strategy: object,
    definition_store: ResearchDefinitionStore | None,
    *,
    policy_set: object | None = None,
) -> ResearchDefinitionSnapshot:
    capture = getattr(strategy, "capture_research_definition", None)
    if not callable(capture):
        raise ValueError("qualification experiment is not snapshot-aware")
    store = definition_store or ResearchDefinitionStore(Path(".research-data/blobs"))
    definition = capture(store, policy_set) if policy_set is not None else capture(store)
    if not isinstance(definition, ResearchDefinitionSnapshot):
        raise ValueError("qualification experiment returned invalid definition evidence")
    return definition


def _declare_trial(strategy: object) -> ExperimentTrialDeclaration:
    declare = getattr(strategy, "declare_experiment_trial", None)
    if not callable(declare):
        raise ValueError("qualification experiment has no declared trial family")
    declaration = declare()
    if not isinstance(declaration, ExperimentTrialDeclaration):
        raise ValueError("qualification experiment returned an invalid trial declaration")
    return declaration


def _registered_family_trial_ids(
    state: Mapping[str, object],
    *,
    experiment_family: str,
    boundary_time: datetime | None,
) -> tuple[str, ...]:
    raw_trials = state.get("trials")
    if not isinstance(raw_trials, list):
        raise ValueError("qualification requires a verified trial registry")
    trial_ids: list[str] = []
    for trial in raw_trials:
        if not isinstance(trial, Mapping) or trial.get("experiment_family") != experiment_family:
            continue
        if trial.get("legacy") is True or trial.get("selection_history_incomplete") is True:
            raise ValueError("selected family contains incomplete legacy trial history")
        trial_id = trial.get("trial_id")
        if not isinstance(trial_id, str) or not trial_id:
            raise ValueError("selected family contains an invalid trial identity")
        if boundary_time is not None:
            registered_at = trial.get("first_registered_at")
            if not isinstance(registered_at, str):
                raise ValueError("selection boundary requires trial registration timestamps")
            if parse_timestamp(registered_at) > boundary_time:
                raise ValueError("selected family contains a trial registered after the boundary")
        trial_ids.append(trial_id)
    registered = tuple(sorted(set(trial_ids)))
    if len(registered) != len(trial_ids) or not registered:
        raise ValueError("selected family trial identities must be unique and non-empty")
    return registered


def _load_trial_input(
    experiment_name: str,
    manifest_path: Path,
    *,
    research_data_store: ResearchDataStore,
    definition_store: ResearchDefinitionStore,
    workflow_path: Path | None,
) -> tuple[str, str, CanonicalSleeveInput, str, date]:
    strategy, policy_set = _resolve_qualification_definition(
        experiment_name=None if "/" in experiment_name else experiment_name,
        research_identity=experiment_name if "/" in experiment_name else None,
        workflow_path=workflow_path,
    )
    definition = _capture_definition(strategy, definition_store, policy_set=policy_set)
    declaration = _declare_trial(strategy)
    snapshot = research_data_store.load_snapshot(manifest_path)
    if snapshot.manifest.definition != definition.blob:
        raise ValueError(f"{experiment_name} snapshot does not match its current exact definition")
    runner = getattr(strategy, "run_with_bundle", None)
    if not callable(runner):
        raise ValueError(f"{experiment_name} has no snapshot-aware runner")
    result = runner(snapshot.bundle)
    sleeve_input = result.get("canonical_sleeve_input") if isinstance(result, Mapping) else None
    if not isinstance(sleeve_input, CanonicalSleeveInput):
        raise ValueError(f"{experiment_name} did not produce canonical sleeve input")
    return (
        formal_trial_id(declaration.family, definition.fingerprint),
        declaration.family,
        sleeve_input,
        snapshot.manifest.snapshot_id,
        snapshot.manifest.decision_time.session,
    )


def _resolve_qualification_definition(
    *,
    experiment_name: str | None,
    research_identity: str | None,
    workflow_path: Path | None,
) -> tuple[object, object | None]:
    if (experiment_name is None) == (research_identity is None):
        raise ValueError(
            "qualification requires exactly one legacy experiment or research identity"
        )
    if research_identity is None:
        return get_experiment(str(experiment_name)), None
    if workflow_path is None:
        raise ValueError("workflow-native qualification requires an exact released workflow")
    return (
        ResearchDefinitionRegistry().load(research_identity),
        resolve_workflow_policy_set(workflow_path),
    )


def _require_retrospective_workflow(
    workflow_path: Path | None,
    *,
    evidence_role: str = "retrospective-confirmatory",
) -> None:
    if workflow_path is None:
        raise ValueError("retrospective qualification requires an exact released workflow")
    contract = Path(workflow_path) / "WORKFLOW.md"
    try:
        text = contract.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read retrospective workflow contract: {exc}") from exc
    required_marker = (
        "study-time-retrospective"
        if evidence_role == "study-time-retrospective"
        else "Optional retrospective-confirmatory checkpoint"
    )
    if required_marker not in text:
        raise ValueError("released workflow does not authorize retrospective qualification")


def _verify_formal_snapshot_observation(
    state: Mapping[str, object],
    *,
    trial_id: str,
    snapshot_id: str,
    minimum_observation_date: date,
    allowed_run_modes: frozenset[str],
) -> None:
    raw_trials = state.get("trials")
    if not isinstance(raw_trials, list):
        raise ValueError("qualification requires a verified trial registry")
    trial = next(
        (
            item
            for item in raw_trials
            if isinstance(item, Mapping) and item.get("trial_id") == trial_id
        ),
        None,
    )
    observations = trial.get("observations") if isinstance(trial, Mapping) else None
    if not isinstance(observations, list) or not any(
        isinstance(observation, Mapping)
        and observation.get("event") == "observation"
        and observation.get("snapshot_id") == snapshot_id
        and observation.get("run_mode") in allowed_run_modes
        and observation.get("outcome_status") == "succeeded"
        and observation.get("validity_status") == "valid"
        and isinstance(observation.get("observed_at"), str)
        and parse_timestamp(str(observation["observed_at"])).date() >= minimum_observation_date
        for observation in observations
    ):
        raise ValueError(
            f"trial {trial_id} has no valid formal observation for snapshot {snapshot_id}"
        )


def _verify_snapshot_cutoff(
    *,
    data_cutoff: date,
    evaluation_end: date,
    experiment_name: str,
    exact: bool,
) -> None:
    if exact and data_cutoff != evaluation_end:
        raise ValueError(
            f"{experiment_name} snapshot cutoff differs from the frozen evaluation end"
        )
    if not exact and data_cutoff < evaluation_end:
        raise ValueError(f"{experiment_name} snapshot does not cover the frozen evaluation")


def _daily_excess_returns(
    plan: HistoricalQualificationPlan,
    sleeve_input: CanonicalSleeveInput,
) -> tuple[DailyExcessReturn, ...]:
    evaluation = evaluate_canonical_sleeve_input(
        sleeve_input,
        base_policy=plan.base_cost_policy,
        stress_policy=plan.stress_cost_policy,
    )
    returns = {
        point.date.date(): 0.0 if point.daily_return is None else point.daily_return
        for point in evaluation.scenarios.base_net.daily_equity
    }
    missing = tuple(session for session in plan.evaluation_sessions if session not in returns)
    if missing:
        raise ValueError(
            f"canonical sleeve evidence does not cover frozen session {missing[0].isoformat()}"
        )
    return tuple(
        DailyExcessReturn(session=session, value=returns[session])
        for session in plan.evaluation_sessions
    )


def _verify_baseline_input(
    trial_id: str,
    baseline: CanonicalSleeveInput,
    *,
    expected_trial_id: str,
    expected_input: CanonicalSleeveInput,
) -> None:
    if trial_id != expected_trial_id or baseline is not expected_input:
        raise ValueError("family baseline input differs from verified frozen evidence")
