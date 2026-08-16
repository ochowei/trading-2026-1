import json
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pandas as pd
import pytest

from trading.core.qualification import (
    HISTORICAL_QUALIFICATION_GATE_NAMES,
    CanonicalSimulatedFill,
    EvaluationEvidenceAudit,
    EvaluationFold,
    ForwardSelectionEpoch,
    HistoricalAggregateEvidence,
    HistoricalBenchmarkEvidence,
    HistoricalBenchmarkPolicy,
    HistoricalFoldEvidence,
    HistoricalQualificationPlan,
    HistoricalScreenResult,
    HistoricalScreenThresholds,
    QualificationGate,
    QualificationRoleCalendar,
    RetrospectiveSelectionCheckpoint,
    SelectionAdjustmentPolicy,
    SelectionAdjustmentResult,
    ShadowActivationPolicy,
    ShadowEvidence,
    ShadowPaperProposal,
    ShadowRegistration,
    StudyQualificationIdentity,
    evaluate_shadow_activation,
)
from trading.core.sleeve_engine import ExecutionCostPolicy
from trading.research_data.qualification_registry import (
    QualificationRegistry,
    QualificationRegistryError,
    _historical_plan_from_payload,
    _historical_plan_payload,
)


def _historical_lifecycle() -> tuple[HistoricalQualificationPlan, HistoricalScreenResult]:
    folds = tuple(
        EvaluationFold(
            fold_id=f"fold-{year}",
            evaluation_year=year,
            outcome_start=date(year, 1, 1),
            outcome_end=date(year, 12, 31),
            signal_start=date(year, 1, 4),
            signal_end=date(year, 12, 28),
        )
        for year in range(2021, 2026)
    )
    plan = HistoricalQualificationPlan(
        plan_id="historical-plan-1",
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        development_years=(2018, 2019, 2020),
        evaluation_sessions=tuple(
            timestamp.date() for timestamp in pd.bdate_range("2021-01-01", "2025-12-31")
        ),
        folds=folds,
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit=Decimal("0.20"),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
        thresholds=HistoricalScreenThresholds(),
        benchmarks=HistoricalBenchmarkPolicy(
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=10,
        ),
        selection_adjustment=SelectionAdjustmentPolicy(
            repetitions=100,
            block_sessions=5,
        ),
    )
    fold_evidence = tuple(
        HistoricalFoldEvidence(
            fold_id=fold.fold_id,
            evaluation_year=fold.evaluation_year,
            signal_count=4,
            candidate_count=4,
            completed_trades=4,
            cumulative_return=0.01,
            stress_cumulative_return=0.005,
            stress_max_drawdown=-0.01,
            gross_profit=1.0,
            gross_loss=0.0,
            stress_gross_profit=0.5,
            stress_gross_loss=0.0,
        )
        for fold in folds
    )
    selection = SelectionAdjustmentResult(
        selected_trial_id="trial-1",
        included_trial_ids=("trial-1", "trial-baseline"),
        observed_mean_excess_return=Decimal("0.001"),
        adjusted_confidence=Decimal("0.95"),
        repetitions=100,
        block_sessions=5,
        passed=True,
    )
    screen = HistoricalScreenResult(
        plan_id=plan.plan_id,
        folds=fold_evidence,
        aggregate=HistoricalAggregateEvidence(
            completed_trades=20,
            traded_folds=5,
            positive_traded_fold_rate=1.0,
            cumulative_return=0.051,
            profit_factor="Infinity",
            stress_cumulative_return=0.025,
            stress_profit_factor="Infinity",
            stress_max_drawdown=-0.01,
            trade_fold_concentration=0.2,
            profit_fold_concentration=0.2,
        ),
        benchmarks=HistoricalBenchmarkEvidence(
            cash_return=0.0,
            family_baseline_return=0.0,
            random_entry_samples=(),
        ),
        selection_adjustment=selection,
        gates=tuple(
            QualificationGate(name, True, "pass", "pass")
            for name in HISTORICAL_QUALIFICATION_GATE_NAMES
        ),
        passed=True,
        disposition="shadow-eligible",
    )
    return plan, screen


def test_legacy_plan_with_additional_earlier_development_year_round_trips(tmp_path) -> None:
    registry = QualificationRegistry(tmp_path / "qualification_registry.json")
    plan, _screen = _historical_lifecycle()
    plan = replace(
        plan,
        plan_id="historical-plan-extra-development",
        development_years=(2017, 2018, 2019, 2020),
    )

    registry.register_historical_plan(plan)

    assert registry.historical_plan(plan.plan_id) == plan
    event = registry.read()["events"][0]
    assert "role_calendar" not in event["payload"]


def test_qualification_registry_appends_shadow_lifecycle_idempotently(tmp_path) -> None:
    current_definition = "a" * 64
    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        definition_verifier=lambda _digest, _size, _fingerprint: None,
        current_definition_resolver=lambda _family, _trial: current_definition,
        now=lambda: datetime(2026, 8, 6, 21, tzinfo=UTC),
    )
    plan, screen = _historical_lifecycle()
    registration = ShadowRegistration(
        shadow_id="shadow-1",
        trial_id="trial-1",
        historical_plan_id="historical-plan-1",
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        prospective_start=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
        activation_policy=ShadowActivationPolicy(
            stress_drawdown_limit=Decimal("0.20"),
        ),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    evidence = ShadowEvidence(
        shadow_id="shadow-1",
        definition_fingerprint="a" * 64,
        as_of=date(2027, 8, 10),
        data_cutoff=date(2027, 8, 10),
        completed_sessions=252,
        paper_proposals=(
            ShadowPaperProposal(
                proposal_id="proposal-1",
                shadow_id="shadow-1",
                signal_date=date(2027, 1, 4),
                entry_date=date(2027, 1, 5),
            ),
        ),
        simulated_fills=(),
        cumulative_return=0.0,
        profit_factor="0.0",
        stress_cumulative_return=0.0,
        stress_profit_factor="0.0",
        stress_max_drawdown=0.0,
        critical_drift=False,
    )
    activation = evaluate_shadow_activation(
        registration,
        evidence,
        current_definition_fingerprint=registration.definition_fingerprint,
    )

    registry.register_historical_plan(plan)
    registry.register_historical_plan(plan)
    assert registry.historical_plan(plan.plan_id) == plan
    historical_event = next(
        event for event in registry.read()["events"] if event["event_type"] == "historical_plan"
    )
    assert "role_calendar" not in historical_event["payload"]
    registry.record_historical_screen(
        screen,
        evaluated_at=datetime(2026, 1, 5, 21, tzinfo=UTC),
    )
    registry.record_historical_screen(
        screen,
        evaluated_at=datetime(2026, 1, 5, 21, tzinfo=UTC),
    )
    with pytest.raises(QualificationRegistryError, match="formal registry time"):
        registry.register_shadow(
            replace(
                registration,
                shadow_id="shadow-early",
                prospective_start=registration.prospective_start - timedelta(seconds=1),
            )
        )
    registry.register_shadow(registration)
    registry.register_shadow(registration)
    with pytest.raises(QualificationRegistryError, match="proposal"):
        registry.record_shadow_evidence(
            replace(
                evidence,
                simulated_fills=(
                    CanonicalSimulatedFill(
                        proposal_id="missing-proposal",
                        quantity=1.0,
                        executed_entry_price=100.0,
                        executed_exit_price=101.0,
                        pnl=1.0,
                    ),
                ),
            )
        )
    with pytest.raises(QualificationRegistryError, match="outside prospective evidence"):
        registry.record_shadow_evidence(
            replace(
                evidence,
                paper_proposals=(
                    replace(
                        evidence.paper_proposals[0],
                        entry_date=evidence.data_cutoff + timedelta(days=1),
                    ),
                ),
            )
        )
    registry.record_shadow_evidence(evidence)
    registry.record_shadow_evidence(evidence)
    with pytest.raises(QualificationRegistryError, match="cannot decrease"):
        registry.record_shadow_evidence(
            replace(
                evidence,
                as_of=evidence.as_of + timedelta(days=1),
                data_cutoff=evidence.data_cutoff + timedelta(days=1),
                completed_sessions=251,
            )
        )
    with pytest.raises(QualificationRegistryError, match="cannot be rewritten"):
        registry.record_shadow_evidence(
            replace(
                evidence,
                as_of=evidence.as_of + timedelta(days=1),
                data_cutoff=evidence.data_cutoff + timedelta(days=1),
                completed_sessions=253,
                paper_proposals=(),
            )
        )
    with pytest.raises(QualificationRegistryError, match="cannot backfill"):
        registry.record_shadow_evidence(
            replace(
                evidence,
                as_of=evidence.as_of + timedelta(days=2),
                data_cutoff=evidence.data_cutoff + timedelta(days=2),
                completed_sessions=254,
                paper_proposals=(
                    *evidence.paper_proposals,
                    ShadowPaperProposal(
                        proposal_id="proposal-backfill",
                        shadow_id=evidence.shadow_id,
                        signal_date=evidence.as_of,
                        entry_date=evidence.as_of + timedelta(days=1),
                    ),
                ),
            )
        )
    with pytest.raises(QualificationRegistryError, match="gates"):
        registry.record_activation_evaluation(
            replace(
                activation,
                eligible=True,
                disposition="activation-eligible",
            ),
            evaluated_at=evidence.as_of,
        )
    with pytest.raises(QualificationRegistryError, match="prospective evidence"):
        registry.record_activation_evaluation(
            replace(
                activation,
                gates=tuple(replace(gate, passed=True) for gate in activation.gates),
                eligible=True,
                disposition="activation-eligible",
            ),
            evaluated_at=evidence.as_of,
        )
    current_definition = "b" * 64
    with pytest.raises(QualificationRegistryError, match="prospective evidence"):
        registry.record_activation_evaluation(activation, evaluated_at=evidence.as_of)
    current_definition = "a" * 64
    registry.record_activation_evaluation(activation, evaluated_at=evidence.as_of)
    registry.record_activation_evaluation(activation, evaluated_at=evidence.as_of)

    events = registry.read()["events"]
    assert [event["event_type"] for event in events] == [
        "historical_plan",
        "historical_screen",
        "shadow_registration",
        "shadow_evidence",
        "activation_evaluation",
    ]
    assert [event["sequence"] for event in events] == [1, 2, 3, 4, 5]
    assert events[0]["payload"]["thresholds"]["minimum_completed_trades"] == 20
    assert events[1]["payload"]["selection_adjustment"]["selected_trial_id"] == "trial-1"
    assert events[2]["payload"]["definition_fingerprint"] == "a" * 64
    assert events[3]["payload"]["completed_sessions"] == 252
    assert events[4]["payload"]["authorized_for_live_orders"] is False
    assert registry.checkpoint_path.exists()

    sections = registry.result_sections(
        historical_plan_id=plan.plan_id,
        shadow_id=registration.shadow_id,
    )
    assert sections["development_summary"]["historical_plan"]["plan_id"] == plan.plan_id
    assert len(sections["historical_stability_folds"]) == 5
    assert sections["shadow_evidence"]["registration"]["shadow_id"] == "shadow-1"
    assert sections["shadow_evidence"]["activation"]["authorized_for_live_orders"] is False

    registry.record_shadow_evidence(
        replace(
            evidence,
            as_of=evidence.as_of + timedelta(days=1),
            data_cutoff=evidence.data_cutoff + timedelta(days=1),
            completed_sessions=253,
        )
    )
    latest = registry.result_sections(
        historical_plan_id=plan.plan_id,
        shadow_id=registration.shadow_id,
    )
    assert latest["shadow_evidence"]["evidence"]["completed_sessions"] == 253
    assert latest["shadow_evidence"]["activation"] == {}


def test_qualification_registry_rejects_shadow_without_persisted_passing_screen(tmp_path) -> None:
    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        definition_verifier=lambda _digest, _size, _fingerprint: None,
        now=lambda: datetime(2026, 8, 6, 21, tzinfo=UTC),
    )
    plan, _screen = _historical_lifecycle()
    registration = ShadowRegistration(
        shadow_id="shadow-1",
        trial_id="trial-1",
        historical_plan_id=plan.plan_id,
        experiment_family=plan.experiment_family,
        definition_fingerprint=plan.definition_fingerprint,
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        prospective_start=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
        activation_policy=ShadowActivationPolicy(stress_drawdown_limit=Decimal("0.20")),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    registry.register_historical_plan(plan)

    with pytest.raises(QualificationRegistryError, match="historical_screen"):
        registry.register_shadow(registration)


def test_retrospective_registry_rejects_missing_or_dual_selection_boundaries(tmp_path) -> None:
    frozen_at = datetime(2026, 8, 6, 21, tzinfo=UTC)
    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        now=lambda: frozen_at,
    )
    historical_plan, _screen = _historical_lifecycle()
    checkpoint = RetrospectiveSelectionCheckpoint(
        frozen_at=frozen_at,
        selected_trial_id="trial-1",
        included_trial_ids=("trial-1", "trial-baseline"),
        prior_selection_history_incomplete=True,
    )
    plan = replace(
        historical_plan,
        plan_id="retrospective-boundary-plan",
        created_at=frozen_at,
        evidence_role="retrospective-confirmatory",
        retrospective_selection_checkpoint=checkpoint,
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=frozen_at,
            justification="Legacy selection provenance is incomplete.",
            trial_history_complete=False,
        ),
    )
    dual = replace(
        plan,
        forward_selection_epoch=ForwardSelectionEpoch(
            started_at=frozen_at,
            selected_trial_id="trial-1",
            included_trial_ids=("trial-1", "trial-baseline"),
            prior_selection_history_incomplete=True,
        ),
    )

    with pytest.raises(QualificationRegistryError, match="two selection boundaries"):
        registry.register_historical_plan(dual)

    missing_payload = _historical_plan_payload(plan)
    missing_payload.pop("retrospective_selection_checkpoint")
    with pytest.raises(QualificationRegistryError, match="frozen trial universe"):
        _historical_plan_from_payload(missing_payload)

    with pytest.raises(QualificationRegistryError, match="two selection boundaries"):
        _historical_plan_from_payload(_historical_plan_payload(dual))


@pytest.mark.parametrize(
    "evidence_role",
    ("retrospective-confirmatory", "study-time-retrospective"),
)
def test_retrospective_registry_round_trip_cannot_register_shadow(
    tmp_path,
    evidence_role: str,
) -> None:
    current_time = [datetime(2026, 8, 6, 21, tzinfo=UTC)]
    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        definition_verifier=lambda _digest, _size, _fingerprint: None,
        now=lambda: current_time[0],
    )
    historical_plan, historical_screen = _historical_lifecycle()
    plan = replace(
        historical_plan,
        plan_id="retrospective-plan-1",
        created_at=current_time[0],
        evidence_role=evidence_role,
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=current_time[0],
            selected_trial_id="trial-1",
            included_trial_ids=("trial-1", "trial-baseline"),
            prior_selection_history_incomplete=True,
        ),
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=current_time[0],
            justification="Legacy selection provenance is incomplete.",
            trial_history_complete=False,
        ),
        role_calendar=QualificationRoleCalendar(
            development_sessions=tuple(
                timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2020-12-31")
            ),
            warmup_sessions=tuple(
                timestamp.date() for timestamp in pd.bdate_range("2017-01-01", "2017-12-31")
            ),
            evaluation_sessions=historical_plan.evaluation_sessions,
        ),
        study_identity=(
            StudyQualificationIdentity(
                study_path="workflows/example--v001/work/studies/example--s001",
                preregistration_sha256="1" * 64,
                plan_sha256="2" * 64,
                candidate_freeze_sha256="3" * 64,
                qualification_spec_sha256="4" * 64,
                workflow_release_sha256="5" * 64,
            )
            if evidence_role == "study-time-retrospective"
            else None
        ),
    )
    screen = replace(
        historical_screen,
        plan_id=plan.plan_id,
        disposition="retrospectively-supported",
    )
    registry.register_historical_plan(plan)
    registry.record_historical_screen(
        screen,
        evaluated_at=datetime(2026, 8, 7, 21, tzinfo=UTC),
    )

    restored = registry.historical_plan(plan.plan_id)
    assert restored == plan
    assert restored.evidence_audit is not None
    assert restored.evidence_audit.classification == "provenance-unknown"

    registration = ShadowRegistration(
        shadow_id="shadow-retrospective",
        trial_id="trial-1",
        historical_plan_id=plan.plan_id,
        experiment_family=plan.experiment_family,
        definition_fingerprint=plan.definition_fingerprint,
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        prospective_start=datetime(2026, 8, 8, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
        activation_policy=ShadowActivationPolicy(stress_drawdown_limit=Decimal("0.20")),
        base_cost_policy=plan.base_cost_policy,
        stress_cost_policy=plan.stress_cost_policy,
    )
    current_time[0] = registration.prospective_start
    with pytest.raises(QualificationRegistryError, match="historical qualification evidence"):
        registry.register_shadow(registration)


def test_qualification_registry_fails_closed_when_definition_snapshot_is_unverifiable(
    tmp_path,
) -> None:
    def reject_snapshot(_digest: str, _size: int, _fingerprint: str) -> None:
        raise ValueError("digest mismatch")

    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        definition_verifier=reject_snapshot,
        now=lambda: datetime(2026, 8, 6, 21, tzinfo=UTC),
    )
    plan, _screen = _historical_lifecycle()
    registration = ShadowRegistration(
        shadow_id="shadow-1",
        trial_id="trial-1",
        historical_plan_id=plan.plan_id,
        experiment_family=plan.experiment_family,
        definition_fingerprint=plan.definition_fingerprint,
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        prospective_start=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
        activation_policy=ShadowActivationPolicy(stress_drawdown_limit=Decimal("0.20")),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )

    with pytest.raises(QualificationRegistryError, match="cannot be verified"):
        registry.register_shadow(registration)

    assert not registry.path.exists()


def test_qualification_registry_rejects_changed_content_for_existing_identity(tmp_path) -> None:
    registry = QualificationRegistry(tmp_path / "qualification_registry.json")
    plan, _screen = _historical_lifecycle()
    registry.register_historical_plan(plan)

    with pytest.raises(QualificationRegistryError, match="conflicts"):
        registry.register_historical_plan(replace(plan, stress_drawdown_limit=Decimal("0.10")))

    state = json.loads(registry.path.read_text(encoding="utf-8"))
    state["events"][0]["payload"]["stress_drawdown_limit"] = "0.05"
    registry.path.write_text(json.dumps(state), encoding="utf-8")
    with pytest.raises(QualificationRegistryError, match="hash"):
        registry.read()


def test_qualification_registry_rejects_removed_hash_chain(tmp_path) -> None:
    registry = QualificationRegistry(tmp_path / "qualification_registry.json")
    plan, _screen = _historical_lifecycle()
    registry.register_historical_plan(plan)

    state = json.loads(registry.path.read_text(encoding="utf-8"))
    state["events"][0].pop("event_hash")
    state["events"][0].pop("previous_hash")
    registry.path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(QualificationRegistryError, match="hash chain is incomplete"):
        registry.read()


def test_qualification_registry_detects_tail_deletion(tmp_path) -> None:
    registry = QualificationRegistry(tmp_path / "qualification_registry.json")
    plan, _screen = _historical_lifecycle()
    registry.register_historical_plan(plan)

    state = json.loads(registry.path.read_text(encoding="utf-8"))
    state["events"].pop()
    registry.path.write_text(json.dumps(state), encoding="utf-8")

    with pytest.raises(QualificationRegistryError, match="head checkpoint"):
        registry.read()


def test_qualification_registry_reverifies_definition_snapshots_on_read(tmp_path) -> None:
    snapshot_available = True

    def verify_snapshot(_digest: str, _size: int, _fingerprint: str) -> None:
        if not snapshot_available:
            raise ValueError("blob missing")

    registry = QualificationRegistry(
        tmp_path / "qualification_registry.json",
        definition_verifier=verify_snapshot,
        now=lambda: datetime(2026, 8, 6, 21, tzinfo=UTC),
    )
    plan, screen = _historical_lifecycle()
    registry.register_historical_plan(plan)
    registry.record_historical_screen(
        screen,
        evaluated_at=datetime(2026, 1, 5, 21, tzinfo=UTC),
    )
    registration = ShadowRegistration(
        shadow_id="shadow-1",
        trial_id="trial-1",
        historical_plan_id=plan.plan_id,
        experiment_family=plan.experiment_family,
        definition_fingerprint=plan.definition_fingerprint,
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        prospective_start=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
        activation_policy=ShadowActivationPolicy(stress_drawdown_limit=Decimal("0.20")),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    registry.register_shadow(registration)

    snapshot_available = False
    with pytest.raises(QualificationRegistryError, match="cannot be verified"):
        registry.read()
