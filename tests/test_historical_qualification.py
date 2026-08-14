from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from itertools import pairwise

import pandas as pd
import pytest

from trading.core.qualification import (
    DailyExcessReturn,
    EvaluationEvidenceAudit,
    ForwardSelectionEpoch,
    HistoricalScreenThresholds,
    RetrospectiveSelectionCheckpoint,
    _qualification_disposition,
    build_historical_qualification_plan,
    evaluate_family_selection_adjustment,
    evaluate_historical_stability_screen,
)
from trading.core.sleeve_engine import (
    CandidateTrade,
    CanonicalSleeveInput,
    ExecutionCostPolicy,
)


def _trial_registry_state(*trial_ids: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "selection_history_incomplete": False,
        "trials": [
            {
                "trial_id": trial_id,
                "experiment_family": "spy:mean-reversion",
                "legacy": False,
                "selection_history_incomplete": False,
            }
            for trial_id in trial_ids
        ],
    }


def _daily_returns(
    value: float,
    sessions: tuple[date, ...],
) -> tuple[DailyExcessReturn, ...]:
    return tuple(DailyExcessReturn(session=session, value=value) for session in sessions)


def test_historical_plan_freezes_development_and_five_non_overlapping_annual_folds() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))

    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=100,
        bootstrap_repetitions=200,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )

    assert plan.development_years == (2018, 2019, 2020)
    assert tuple(fold.evaluation_year for fold in plan.folds) == (2021, 2022, 2023, 2024, 2025)
    assert all(fold.signal_start > fold.outcome_start for fold in plan.folds)
    assert all(fold.signal_end < fold.outcome_end for fold in plan.folds)
    assert all(earlier.outcome_end < later.outcome_start for earlier, later in pairwise(plan.folds))
    assert plan.thresholds.selection_confidence == Decimal("0.9")
    assert plan.stress_drawdown_limit == Decimal("0.2")
    assert plan.benchmarks.family_baseline_trial_id == "trial-baseline"
    assert plan.benchmarks.random_seed == 17
    assert plan.selection_adjustment.repetitions == 200
    assert plan.selection_adjustment.block_sessions == 5
    assert plan.plan_id.startswith("historical-plan-")
    assert plan.created_at == datetime(2020, 12, 31, 21, tzinfo=UTC)
    assert plan.folds[0].contains_signal(date(2021, 1, 5))


@pytest.mark.parametrize(
    ("session_start", "session_end", "evaluation_years", "message"),
    [
        ("2019-01-01", "2025-12-31", (2021, 2022, 2023, 2024, 2025), "development"),
        ("2018-01-01", "2024-12-31", (2021, 2022, 2023, 2024), "five"),
    ],
)
def test_historical_plan_rejects_insufficient_development_or_evaluation_years(
    session_start: str,
    session_end: str,
    evaluation_years: tuple[int, ...],
    message: str,
) -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range(session_start, session_end))

    with pytest.raises(ValueError, match=message):
        build_historical_qualification_plan(
            experiment_family="spy:mean-reversion",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=evaluation_years,
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=100,
            bootstrap_repetitions=200,
            bootstrap_block_sessions=5,
            created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
            base_cost_policy=ExecutionCostPolicy(),
            stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
        )


def test_historical_plan_must_be_frozen_before_the_first_evaluation_outcome() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))

    with pytest.raises(ValueError, match="before evaluation"):
        build_historical_qualification_plan(
            experiment_family="spy:mean-reversion",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=(2021, 2022, 2023, 2024, 2025),
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=10,
            bootstrap_repetitions=20,
            bootstrap_block_sessions=5,
            created_at=datetime(2021, 1, 4, 21, tzinfo=UTC),
            base_cost_policy=ExecutionCostPolicy(),
            stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
        )


def test_clean_historical_plan_rejects_unknown_or_incomplete_provenance() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    frozen_at = datetime(2020, 12, 31, 21, tzinfo=UTC)

    with pytest.raises(ValueError, match="verified-clean complete provenance"):
        build_historical_qualification_plan(
            experiment_family="spy:mean-reversion",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=(2021, 2022, 2023, 2024, 2025),
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=10,
            bootstrap_repetitions=20,
            bootstrap_block_sessions=5,
            created_at=frozen_at,
            evidence_audit=EvaluationEvidenceAudit(
                classification="provenance-unknown",
                frozen_at=frozen_at,
                justification="Legacy selection history cannot be verified.",
                trial_history_complete=False,
            ),
        )


def test_retrospective_plan_accepts_completed_unknown_provenance_without_promotion() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    frozen_at = datetime(2026, 8, 13, 7, tzinfo=UTC)

    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=frozen_at,
        evidence_role="retrospective-confirmatory",
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=frozen_at,
            selected_trial_id="trial-selected",
            included_trial_ids=("trial-baseline", "trial-selected"),
            prior_selection_history_incomplete=True,
        ),
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=frozen_at,
            justification="Completed data are useful only for bounded falsification.",
            trial_history_complete=False,
        ),
    )

    assert plan.plan_id.startswith("retrospective-plan-")
    assert plan.evidence_role == "retrospective-confirmatory"
    assert plan.evidence_audit is not None
    assert plan.evidence_audit.classification == "provenance-unknown"
    assert _qualification_disposition(plan.evidence_role, True) == "retrospectively-supported"
    assert _qualification_disposition(plan.evidence_role, False) == "retrospective-screen-failed"


def test_retrospective_plan_requires_exactly_one_retrospective_boundary() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    frozen_at = datetime(2026, 8, 13, 7, tzinfo=UTC)
    audit = EvaluationEvidenceAudit(
        classification="provenance-unknown",
        frozen_at=frozen_at,
        justification="Completed data are retrospective-confirmatory only.",
        trial_history_complete=False,
    )
    kwargs = {
        "experiment_family": "spy:mean-reversion",
        "definition_fingerprint": "a" * 64,
        "sessions": sessions,
        "evaluation_years": (2021, 2022, 2023, 2024, 2025),
        "maximum_holding_sessions": 1,
        "execution_lag_sessions": 1,
        "dependency_sessions": 2,
        "embargo_sessions": 1,
        "stress_drawdown_limit": "0.20",
        "family_baseline_trial_id": "trial-baseline",
        "random_seed": 17,
        "random_samples": 10,
        "bootstrap_repetitions": 20,
        "bootstrap_block_sessions": 5,
        "created_at": frozen_at,
        "evidence_role": "retrospective-confirmatory",
        "evidence_audit": audit,
    }

    with pytest.raises(ValueError, match="frozen trial universe"):
        build_historical_qualification_plan(**kwargs)

    with pytest.raises(ValueError, match="two selection boundaries"):
        build_historical_qualification_plan(
            **kwargs,
            forward_selection_epoch=ForwardSelectionEpoch(
                started_at=frozen_at,
                selected_trial_id="trial-selected",
                included_trial_ids=("trial-baseline", "trial-selected"),
                prior_selection_history_incomplete=True,
            ),
            retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
                frozen_at=frozen_at,
                selected_trial_id="trial-selected",
                included_trial_ids=("trial-baseline", "trial-selected"),
                prior_selection_history_incomplete=True,
            ),
        )


def test_retrospective_plan_freezes_explicit_later_development_and_prior_warmup() -> None:
    evaluation_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2010-01-01", "2014-12-31")
    )
    development_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2015-01-01", "2025-12-31")
    )
    warmup_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2009-01-01", "2009-12-31")
    )
    frozen_at = datetime(2026, 8, 13, 7, tzinfo=UTC)

    plan = build_historical_qualification_plan(
        experiment_family="fxi:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=evaluation_sessions,
        evaluation_years=(2010, 2011, 2012, 2013, 2014),
        maximum_holding_sessions=20,
        execution_lag_sessions=1,
        dependency_sessions=21,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=20260813,
        random_samples=1000,
        bootstrap_repetitions=1000,
        bootstrap_block_sessions=20,
        created_at=frozen_at,
        evidence_role="retrospective-confirmatory",
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=frozen_at,
            selected_trial_id="trial-selected",
            included_trial_ids=("trial-baseline", "trial-selected"),
            prior_selection_history_incomplete=True,
        ),
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=frozen_at,
            justification="Legacy selection provenance is incomplete.",
            trial_history_complete=False,
        ),
        development_sessions=development_sessions,
        warmup_sessions=warmup_sessions,
    )

    assert plan.development_years == tuple(range(2015, 2026))
    assert plan.role_calendar is not None
    assert plan.role_calendar.development_sessions == development_sessions
    assert plan.role_calendar.warmup_sessions == warmup_sessions
    assert plan.role_calendar.evaluation_sessions == evaluation_sessions


def test_explicit_role_calendar_rejects_overlapping_or_non_retrospective_roles() -> None:
    evaluation_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2010-01-01", "2014-12-31")
    )
    development_sessions = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2015-01-01", "2017-12-31")
    )
    frozen_at = datetime(2026, 8, 13, 7, tzinfo=UTC)
    kwargs = {
        "experiment_family": "fxi:mean-reversion",
        "definition_fingerprint": "a" * 64,
        "sessions": evaluation_sessions,
        "evaluation_years": (2010, 2011, 2012, 2013, 2014),
        "maximum_holding_sessions": 20,
        "execution_lag_sessions": 1,
        "dependency_sessions": 21,
        "embargo_sessions": 1,
        "stress_drawdown_limit": "0.20",
        "family_baseline_trial_id": "trial-baseline",
        "random_seed": 17,
        "random_samples": 10,
        "bootstrap_repetitions": 20,
        "bootstrap_block_sessions": 5,
        "created_at": frozen_at,
        "development_sessions": development_sessions,
    }

    with pytest.raises(ValueError, match="only valid for retrospective"):
        build_historical_qualification_plan(
            **kwargs,
            warmup_sessions=(date(2009, 1, 2),),
        )

    checkpoint = RetrospectiveSelectionCheckpoint(
        frozen_at=frozen_at,
        selected_trial_id="trial-selected",
        included_trial_ids=("trial-baseline", "trial-selected"),
        prior_selection_history_incomplete=True,
    )
    audit = EvaluationEvidenceAudit(
        classification="provenance-unknown",
        frozen_at=frozen_at,
        justification="Legacy selection provenance is incomplete.",
        trial_history_complete=False,
    )
    overlapping_development = tuple(
        timestamp.date() for timestamp in pd.bdate_range("2010-01-01", "2012-12-31")
    )
    with pytest.raises(ValueError, match="must not overlap"):
        build_historical_qualification_plan(
            **{
                **kwargs,
                "development_sessions": overlapping_development,
                "evidence_role": "retrospective-confirmatory",
                "retrospective_selection_checkpoint": checkpoint,
                "evidence_audit": audit,
            },
            warmup_sessions=tuple(
                timestamp.date() for timestamp in pd.bdate_range("2009-01-01", "2009-12-31")
            ),
        )


def test_historical_plan_rejects_sparse_year_labels_that_are_not_annual_periods() -> None:
    sessions = tuple(
        timestamp.date()
        for timestamp in pd.bdate_range("2018-01-01", "2025-12-31")
        if timestamp.year != 2022 or timestamp.month == 1
    )

    with pytest.raises(ValueError, match="complete annual"):
        build_historical_qualification_plan(
            experiment_family="spy:mean-reversion",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=(2021, 2022, 2023, 2024, 2025),
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=10,
            bootstrap_repetitions=20,
            bootstrap_block_sessions=5,
            created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
            base_cost_policy=ExecutionCostPolicy(),
            stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
        )


def test_historical_plan_rejects_thresholds_weaker_than_phase_six_specification() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))

    with pytest.raises(ValueError, match="minimum_completed_trades"):
        build_historical_qualification_plan(
            experiment_family="spy:mean-reversion",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=(2021, 2022, 2023, 2024, 2025),
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id="trial-baseline",
            random_seed=17,
            random_samples=10,
            bootstrap_repetitions=20,
            bootstrap_block_sessions=5,
            created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
            base_cost_policy=ExecutionCostPolicy(),
            stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
            thresholds=replace(
                HistoricalScreenThresholds(),
                minimum_completed_trades=19,
            ),
        )


def test_historical_screen_attributes_completed_trades_by_signal_date_and_keeps_empty_folds() -> (
    None
):
    calendar = pd.bdate_range("2018-01-01", "2025-12-31")
    sessions = tuple(timestamp.date() for timestamp in calendar)
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    trade = CandidateTrade(
        signal_date=date(2021, 1, 5),
        entry_date=date(2021, 1, 6),
        entry_price=100.0,
        exit_date=date(2021, 1, 7),
        exit_price=110.0,
        exit_type="target",
    )
    prices = pd.Series(100.0, index=calendar)
    strategy_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(trade,),
        raw_signals=(trade.signal_date,),
        legacy_signals=(trade.signal_date,),
        legacy_candidates=(trade,),
    )
    baseline_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(),
        raw_signals=(),
        legacy_signals=(),
        legacy_candidates=(),
    )
    selection_adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id="trial-selected",
        trial_registry_state=_trial_registry_state("trial-selected", "trial-baseline"),
        trial_daily_excess_returns={
            "trial-selected": _daily_returns(0.02, plan.evaluation_sessions),
            "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
        },
    )

    result = evaluate_historical_stability_screen(
        plan,
        strategy_input=strategy_input,
        family_baseline_trial_id="trial-baseline",
        family_baseline_input=baseline_input,
        family_baseline_verifier=lambda _trial_id, _input: None,
        selection_adjustment=selection_adjustment,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
    )

    assert len(result.folds) == 5
    assert result.folds[0].completed_trades == 1
    assert result.folds[0].cumulative_return == pytest.approx(0.10)
    assert all(fold.completed_trades == 0 for fold in result.folds[1:])
    assert all(fold.visible for fold in result.folds)
    assert len(result.benchmarks.random_entry_samples) == 10
    assert all(sample.completed_trades == 1 for sample in result.benchmarks.random_entry_samples)
    assert all(sample.entry_months == (1,) for sample in result.benchmarks.random_entry_samples)
    assert all(sample.holding_sessions == (1,) for sample in result.benchmarks.random_entry_samples)
    repeated = evaluate_historical_stability_screen(
        plan,
        strategy_input=strategy_input,
        family_baseline_trial_id="trial-baseline",
        family_baseline_input=baseline_input,
        family_baseline_verifier=lambda _trial_id, _input: None,
        selection_adjustment=selection_adjustment,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
    )
    assert repeated.benchmarks.random_entry_samples == result.benchmarks.random_entry_samples
    assert result.selection_adjustment == selection_adjustment
    assert any(gate.name == "selection_adjusted_confidence" for gate in result.gates)
    assert result.disposition != "active"

    with pytest.raises(ValueError, match="selection adjustment policy"):
        evaluate_historical_stability_screen(
            plan,
            strategy_input=strategy_input,
            family_baseline_trial_id="trial-baseline",
            family_baseline_input=baseline_input,
            family_baseline_verifier=lambda _trial_id, _input: None,
            selection_adjustment=replace(selection_adjustment, repetitions=19),
            base_policy=ExecutionCostPolicy(),
            stress_policy=ExecutionCostPolicy(
                entry_slippage_bps=10,
                exit_slippage_bps=10,
                fee_bps_per_side=1,
            ),
        )


def test_family_selection_adjustment_is_deterministic_and_includes_every_registered_trial() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    trial_returns = {
        "trial-selected": _daily_returns(0.02, plan.evaluation_sessions),
        "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
        "trial-sibling": _daily_returns(-0.01, plan.evaluation_sessions),
    }

    adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id="trial-selected",
        trial_registry_state=_trial_registry_state(
            "trial-selected", "trial-baseline", "trial-sibling"
        ),
        trial_daily_excess_returns=trial_returns,
    )
    repeated = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id="trial-selected",
        trial_registry_state=_trial_registry_state(
            "trial-selected", "trial-baseline", "trial-sibling"
        ),
        trial_daily_excess_returns=trial_returns,
    )

    assert adjustment == repeated
    assert adjustment.included_trial_ids == (
        "trial-baseline",
        "trial-selected",
        "trial-sibling",
    )
    assert adjustment.adjusted_confidence > Decimal("0.90")
    assert adjustment.passed

    shifted = tuple(
        replace(observation, session=observation.session + timedelta(days=1))
        for observation in trial_returns["trial-sibling"]
    )
    with pytest.raises(ValueError, match="identical sessions"):
        evaluate_family_selection_adjustment(
            plan,
            selected_trial_id="trial-selected",
            trial_registry_state=_trial_registry_state(
                "trial-selected", "trial-baseline", "trial-sibling"
            ),
            trial_daily_excess_returns={**trial_returns, "trial-sibling": shifted},
        )


def test_family_selection_adjustment_fails_closed_for_incomplete_trial_history() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    registry_state = _trial_registry_state("trial-selected", "trial-baseline")
    registry_state["selection_history_incomplete"] = True

    with pytest.raises(ValueError, match="incomplete"):
        evaluate_family_selection_adjustment(
            plan,
            selected_trial_id="trial-selected",
            trial_registry_state=registry_state,
            trial_daily_excess_returns={
                "trial-selected": _daily_returns(0.02, plan.evaluation_sessions),
                "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
            },
        )


def test_family_selection_adjustment_accepts_retrospective_checkpoint() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    frozen_at = datetime(2026, 1, 2, 21, tzinfo=UTC)
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=frozen_at,
        evidence_role="retrospective-confirmatory",
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=frozen_at,
            selected_trial_id="trial-selected",
            included_trial_ids=("trial-baseline", "trial-selected"),
            prior_selection_history_incomplete=True,
        ),
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=frozen_at,
            justification="Completed data are retrospective-confirmatory only.",
            trial_history_complete=False,
        ),
    )
    registry_state = _trial_registry_state("trial-selected", "trial-baseline")
    registry_state["selection_history_incomplete"] = True
    for index, trial in enumerate(registry_state["trials"]):
        trial["first_registered_at"] = f"2020-12-30T{index:02d}:00:00+00:00"

    adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id="trial-selected",
        trial_registry_state=registry_state,
        trial_daily_excess_returns={
            "trial-selected": _daily_returns(0.02, plan.evaluation_sessions),
            "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
        },
    )

    assert adjustment.included_trial_ids == ("trial-baseline", "trial-selected")
    assert adjustment.passed


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("disclosure", "history disclosure"),
        ("family", "trial universe"),
        ("selected", "selected trial"),
        ("missing-timestamp", "registration timestamps"),
        ("late-timestamp", "registered after it was frozen"),
    ],
)
def test_family_selection_adjustment_rejects_invalid_retrospective_boundary(
    case: str,
    message: str,
) -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    frozen_at = datetime(2026, 1, 2, 21, tzinfo=UTC)
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=frozen_at,
        evidence_role="retrospective-confirmatory",
        retrospective_selection_checkpoint=RetrospectiveSelectionCheckpoint(
            frozen_at=frozen_at,
            selected_trial_id="trial-selected",
            included_trial_ids=("trial-baseline", "trial-selected"),
            prior_selection_history_incomplete=True,
        ),
        evidence_audit=EvaluationEvidenceAudit(
            classification="provenance-unknown",
            frozen_at=frozen_at,
            justification="Completed data are retrospective-confirmatory only.",
            trial_history_complete=False,
        ),
    )
    registry_state = _trial_registry_state("trial-selected", "trial-baseline")
    registry_state["selection_history_incomplete"] = True
    for index, trial in enumerate(registry_state["trials"]):
        trial["first_registered_at"] = f"2020-12-30T{index:02d}:00:00+00:00"
    selected_trial_id = "trial-selected"
    if case == "disclosure":
        registry_state["selection_history_incomplete"] = False
    elif case == "family":
        registry_state["trials"].append(
            {
                "trial_id": "trial-extra",
                "experiment_family": "spy:mean-reversion",
                "legacy": False,
                "selection_history_incomplete": False,
                "first_registered_at": "2020-12-30T02:00:00+00:00",
            }
        )
    elif case == "selected":
        selected_trial_id = "trial-baseline"
    elif case == "missing-timestamp":
        registry_state["trials"][0].pop("first_registered_at")
    elif case == "late-timestamp":
        registry_state["trials"][0]["first_registered_at"] = "2026-01-03T00:00:00+00:00"

    with pytest.raises(ValueError, match=message):
        evaluate_family_selection_adjustment(
            plan,
            selected_trial_id=selected_trial_id,
            trial_registry_state=registry_state,
            trial_daily_excess_returns={
                "trial-selected": _daily_returns(0.02, plan.evaluation_sessions),
                "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
            },
        )


def test_family_selection_adjustment_rejects_returns_outside_frozen_folds() -> None:
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    future_returns = tuple(
        DailyExcessReturn(session=timestamp.date(), value=0.01)
        for timestamp in pd.bdate_range("2026-01-05", periods=20)
    )

    with pytest.raises(ValueError, match="frozen evaluation folds"):
        evaluate_family_selection_adjustment(
            plan,
            selected_trial_id="trial-selected",
            trial_registry_state=_trial_registry_state("trial-selected", "trial-baseline"),
            trial_daily_excess_returns={
                "trial-selected": future_returns,
                "trial-baseline": future_returns,
            },
        )


def test_passing_historical_gates_produce_auditable_aggregate_evidence_but_never_active() -> None:
    calendar = pd.bdate_range("2018-01-01", "2025-12-31")
    sessions = tuple(timestamp.date() for timestamp in calendar)
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id="trial-baseline",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=datetime(2020, 12, 31, 21, tzinfo=UTC),
        base_cost_policy=ExecutionCostPolicy(),
        stress_cost_policy=ExecutionCostPolicy(10, 10, 1),
    )
    index_by_date = {timestamp.date(): index for index, timestamp in enumerate(calendar)}
    candidates = []
    for fold in plan.folds:
        eligible = [session for session in sessions if fold.contains_signal(session)]
        for offset in (5, 45, 85, 125):
            signal_date = eligible[offset]
            signal_index = index_by_date[signal_date]
            candidates.append(
                CandidateTrade(
                    signal_date=signal_date,
                    entry_date=calendar[signal_index + 1].date(),
                    entry_price=100.0,
                    exit_date=calendar[signal_index + 2].date(),
                    exit_price=101.0,
                    exit_type="target",
                )
            )
    prices = pd.Series(100.0, index=calendar)
    strategy_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=tuple(candidates),
        raw_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_candidates=tuple(candidates),
    )
    baseline_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(),
        raw_signals=(),
        legacy_signals=(),
        legacy_candidates=(),
    )
    adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id="trial-selected",
        trial_registry_state=_trial_registry_state("trial-selected", "trial-baseline"),
        trial_daily_excess_returns={
            "trial-selected": _daily_returns(0.001, plan.evaluation_sessions),
            "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
        },
    )

    result = evaluate_historical_stability_screen(
        plan,
        strategy_input=strategy_input,
        family_baseline_trial_id="trial-baseline",
        family_baseline_input=baseline_input,
        family_baseline_verifier=lambda _trial_id, _input: None,
        selection_adjustment=adjustment,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
    )

    assert result.aggregate.completed_trades == 20
    assert result.aggregate.traded_folds == 5
    assert result.aggregate.positive_traded_fold_rate == pytest.approx(1.0)
    assert result.aggregate.profit_factor == "Infinity"
    assert result.aggregate.stress_cumulative_return > 0
    assert result.aggregate.stress_profit_factor == "Infinity"
    assert result.aggregate.trade_fold_concentration == pytest.approx(0.20)
    assert result.aggregate.profit_fold_concentration == pytest.approx(0.20)
    assert result.aggregate.stress_max_drawdown >= -0.20
    assert all(gate.passed for gate in result.gates)
    assert any(gate.name == "stress_cumulative_return" for gate in result.gates)
    assert any(gate.name == "stress_profit_factor" for gate in result.gates)
    assert result.passed
    assert result.disposition == "shadow-eligible"

    def reject_unverified_baseline(
        _trial_id: str,
        _input: CanonicalSleeveInput,
    ) -> None:
        raise ValueError("baseline evidence is unverified")

    with pytest.raises(ValueError, match="baseline evidence is unverified"):
        evaluate_historical_stability_screen(
            plan,
            strategy_input=strategy_input,
            family_baseline_trial_id="trial-baseline",
            family_baseline_input=baseline_input,
            family_baseline_verifier=reject_unverified_baseline,
            selection_adjustment=adjustment,
            base_policy=ExecutionCostPolicy(),
            stress_policy=ExecutionCostPolicy(10, 10, 1),
        )

    with pytest.raises(ValueError, match="frozen plan"):
        evaluate_historical_stability_screen(
            plan,
            strategy_input=strategy_input,
            family_baseline_trial_id="trial-baseline",
            family_baseline_input=baseline_input,
            family_baseline_verifier=lambda _trial_id, _input: None,
            selection_adjustment=adjustment,
            base_policy=ExecutionCostPolicy(),
            stress_policy=ExecutionCostPolicy(100, 100, 10),
        )
