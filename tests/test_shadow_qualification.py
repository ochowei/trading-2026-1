from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pandas as pd
import pytest

from trading.core.qualification import (
    DailyExcessReturn,
    build_historical_qualification_plan,
    build_shadow_evidence,
    evaluate_family_selection_adjustment,
    evaluate_historical_stability_screen,
    evaluate_shadow_activation,
    register_shadow,
    restart_shadow_registration,
)
from trading.core.sleeve_engine import (
    CandidateTrade,
    CanonicalSleeveInput,
    ExecutionCostPolicy,
)
from trading.market_data.calendar import PrimaryUSSessionCalendar

_SESSION_CALENDAR = PrimaryUSSessionCalendar()


def _after_session_close(session: date) -> datetime:
    return _SESSION_CALENDAR.decision_time(session) + timedelta(minutes=1)


def _shadow_sessions(start: date, count: int) -> pd.DatetimeIndex:
    first = _SESSION_CALENDAR.session_on_or_after(start)
    last = _SESSION_CALENDAR.session_offset(first, count - 1)
    return _SESSION_CALENDAR.sessions_in_range(first, last)


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


def _passing_historical_screen(
    definition_fingerprint: str = "a" * 64,
    selected_trial_id: str = "trial-selected",
):
    calendar = pd.bdate_range("2018-01-01", "2025-12-31")
    sessions = tuple(timestamp.date() for timestamp in calendar)
    plan = build_historical_qualification_plan(
        experiment_family="spy:mean-reversion",
        definition_fingerprint=definition_fingerprint,
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
                    entry_price=100,
                    exit_date=calendar[signal_index + 2].date(),
                    exit_price=101,
                    exit_type="target",
                )
            )
    prices = pd.Series(100.0, index=calendar)
    strategy = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=tuple(candidates),
        raw_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_candidates=tuple(candidates),
    )
    baseline = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(),
        raw_signals=(),
        legacy_signals=(),
        legacy_candidates=(),
    )
    adjustment = evaluate_family_selection_adjustment(
        plan,
        selected_trial_id=selected_trial_id,
        trial_registry_state=_trial_registry_state(selected_trial_id, "trial-baseline"),
        trial_daily_excess_returns={
            selected_trial_id: _daily_returns(0.02, plan.evaluation_sessions),
            "trial-baseline": _daily_returns(0.0, plan.evaluation_sessions),
        },
    )
    result = evaluate_historical_stability_screen(
        plan,
        strategy_input=strategy,
        family_baseline_trial_id="trial-baseline",
        family_baseline_input=baseline,
        family_baseline_verifier=lambda _trial_id, _input: None,
        selection_adjustment=adjustment,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
    )
    assert result.passed
    return plan, result


def test_shadow_registration_freezes_definition_and_prospective_activation_policy() -> None:
    plan, screen = _passing_historical_screen()

    with pytest.raises(ValueError, match="historical outcomes"):
        register_shadow(
            plan,
            screen,
            trial_id="trial-selected",
            definition_snapshot_id="d" * 64,
            definition_snapshot_byte_count=100,
            registered_at=datetime(2025, 12, 31, 21, tzinfo=UTC),
            activation_checkpoint=date(2027, 8, 9),
        )

    registration = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )
    repeated = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )

    assert registration == repeated
    assert registration.status == "shadow"
    assert registration.definition_fingerprint == "a" * 64
    assert registration.definition_snapshot_id == "d" * 64
    assert registration.prospective_start == datetime(2026, 8, 6, 21, tzinfo=UTC)
    assert registration.activation_policy.minimum_completed_sessions == 252
    assert registration.activation_policy.minimum_completed_trades == 12
    assert registration.activation_policy.minimum_profit_factor == Decimal("1")
    assert registration.shadow_id.startswith("shadow-")


def test_shadow_evidence_starts_after_registration_and_low_frequency_remains_shadow() -> None:
    plan, screen = _passing_historical_screen()
    registration = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )
    calendar = _shadow_sessions(date(2026, 8, 3), 260)
    prices = pd.Series(100.0, index=calendar)
    legacy_part_c = CandidateTrade(
        signal_date=date(2026, 8, 5),
        entry_date=date(2026, 8, 6),
        entry_price=100,
        exit_date=date(2026, 8, 7),
        exit_price=110,
        exit_type="target",
    )
    prospective = CandidateTrade(
        signal_date=date(2026, 8, 7),
        entry_date=date(2026, 8, 10),
        entry_price=100,
        exit_date=date(2026, 8, 11),
        exit_price=110,
        exit_type="target",
    )
    sleeve_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(legacy_part_c, prospective),
        raw_signals=(legacy_part_c.signal_date, prospective.signal_date),
        legacy_signals=(legacy_part_c.signal_date, prospective.signal_date),
        legacy_candidates=(legacy_part_c, prospective),
    )

    evidence = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=sleeve_input,
        as_of=calendar[-1].date(),
        completed_through=calendar[-1].date(),
        observed_at=_after_session_close(calendar[-1].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
        critical_drift=False,
    )
    repeated = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=sleeve_input,
        as_of=calendar[-1].date(),
        completed_through=calendar[-1].date(),
        observed_at=_after_session_close(calendar[-1].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
        critical_drift=False,
    )
    activation = evaluate_shadow_activation(
        registration,
        evidence,
        current_definition_fingerprint=registration.definition_fingerprint,
    )

    assert evidence.completed_sessions >= 252
    assert tuple(proposal.signal_date for proposal in evidence.paper_proposals) == (
        prospective.signal_date,
    )
    assert len(evidence.simulated_fills) == 1
    assert evidence.simulated_fills[0].proposal_id == evidence.paper_proposals[0].proposal_id
    assert evidence.simulated_fills[0].quantity > 0
    assert evidence.definition_fingerprint == registration.definition_fingerprint
    assert repeated.paper_proposals == evidence.paper_proposals
    assert repeated.simulated_fills == evidence.simulated_fills
    assert activation.eligible is False
    assert activation.disposition == "shadow-insufficient-evidence"
    assert any(gate.name == "completed_trades" and not gate.passed for gate in activation.gates)


def test_definition_change_requires_a_new_shadow_registration_without_backfill() -> None:
    plan, screen = _passing_historical_screen()
    original = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )
    new_plan, new_screen = _passing_historical_screen(
        definition_fingerprint="b" * 64,
        selected_trial_id="trial-selected-v2",
    )

    restarted = restart_shadow_registration(
        original,
        new_plan,
        new_screen,
        trial_id="trial-selected-v2",
        definition_snapshot_id="e" * 64,
        definition_snapshot_byte_count=101,
        registered_at=datetime(2027, 1, 4, 21, tzinfo=UTC),
        activation_checkpoint=date(2028, 1, 5),
    )

    assert restarted.shadow_id != original.shadow_id
    assert restarted.prior_shadow_id == original.shadow_id
    assert restarted.definition_fingerprint == "b" * 64
    assert restarted.definition_snapshot_id == "e" * 64
    assert restarted.prospective_start == datetime(2027, 1, 4, 21, tzinfo=UTC)
    assert restarted.activation_policy == original.activation_policy
    assert restarted.status == "shadow"


def test_shadow_fill_links_the_exact_candidate_proposal_and_rejects_future_exit() -> None:
    plan, screen = _passing_historical_screen()
    registration = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )
    calendar = _shadow_sessions(date(2026, 8, 7), 30)
    first = CandidateTrade(
        signal_date=calendar[1].date(),
        entry_date=calendar[2].date(),
        entry_price=100,
        exit_date=calendar[3].date(),
        exit_price=110,
        exit_type="target",
    )
    same_dates_different_terms = replace(first, entry_price=101)
    prices = pd.Series(100.0, index=calendar)
    sleeve_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=(first, same_dates_different_terms),
        raw_signals=(first.signal_date, same_dates_different_terms.signal_date),
        legacy_signals=(first.signal_date, same_dates_different_terms.signal_date),
        legacy_candidates=(first, same_dates_different_terms),
    )

    with pytest.raises(ValueError, match="completed market session"):
        build_shadow_evidence(
            registration,
            current_definition_fingerprint="a" * 64,
            sleeve_input=sleeve_input,
            as_of=calendar[-1].date(),
            completed_through=calendar[-2].date(),
            observed_at=_after_session_close(calendar[-2].date()),
            session_calendar=_SESSION_CALENDAR,
            base_policy=registration.base_cost_policy,
            stress_policy=registration.stress_cost_policy,
            critical_drift=False,
        )

    with pytest.raises(ValueError, match="duplicate proposal"):
        build_shadow_evidence(
            registration,
            current_definition_fingerprint="a" * 64,
            sleeve_input=sleeve_input,
            as_of=calendar[-1].date(),
            completed_through=calendar[-1].date(),
            observed_at=_after_session_close(calendar[-1].date()),
            session_calendar=_SESSION_CALENDAR,
            base_policy=registration.base_cost_policy,
            stress_policy=registration.stress_cost_policy,
            critical_drift=False,
        )

    completed_input = replace(
        sleeve_input,
        candidates=(first,),
        raw_signals=(first.signal_date,),
        legacy_signals=(first.signal_date,),
        legacy_candidates=(first,),
    )
    evidence = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=completed_input,
        as_of=calendar[-1].date(),
        completed_through=calendar[-1].date(),
        observed_at=_after_session_close(calendar[-1].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=registration.base_cost_policy,
        stress_policy=registration.stress_cost_policy,
        critical_drift=False,
    )
    open_candidate = replace(first, exit_date=None, exit_price=None, exit_type=None)
    open_evidence = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=replace(
            completed_input,
            candidates=(open_candidate,),
            legacy_candidates=(open_candidate,),
        ),
        as_of=calendar[2].date(),
        completed_through=calendar[2].date(),
        observed_at=_after_session_close(calendar[2].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=registration.base_cost_policy,
        stress_policy=registration.stress_cost_policy,
        critical_drift=False,
    )

    assert len(evidence.simulated_fills) == 1
    assert evidence.simulated_fills[0].proposal_id == evidence.paper_proposals[0].proposal_id
    assert open_evidence.paper_proposals[0].proposal_id == evidence.paper_proposals[0].proposal_id

    future = replace(first, exit_date=date(2027, 1, 4))
    with pytest.raises(ValueError, match="after the evidence cutoff"):
        build_shadow_evidence(
            registration,
            current_definition_fingerprint="a" * 64,
            sleeve_input=replace(completed_input, candidates=(future,)),
            as_of=calendar[-1].date(),
            completed_through=calendar[-1].date(),
            observed_at=_after_session_close(calendar[-1].date()),
            session_calendar=_SESSION_CALENDAR,
            base_policy=registration.base_cost_policy,
            stress_policy=registration.stress_cost_policy,
            critical_drift=False,
        )


def test_complete_positive_shadow_evidence_is_activation_eligible_but_not_live_authorized() -> None:
    plan, screen = _passing_historical_screen()
    registration = register_shadow(
        plan,
        screen,
        trial_id="trial-selected",
        definition_snapshot_id="d" * 64,
        definition_snapshot_byte_count=100,
        registered_at=datetime(2026, 8, 6, 21, tzinfo=UTC),
        activation_checkpoint=date(2027, 8, 9),
    )
    calendar = _shadow_sessions(date(2026, 8, 3), 270)
    prices = pd.Series(100.0, index=calendar)
    candidates = []
    for index in (5, 25, 45, 65, 85, 105, 125, 145, 165, 185, 205, 225):
        candidates.append(
            CandidateTrade(
                signal_date=calendar[index].date(),
                entry_date=calendar[index + 1].date(),
                entry_price=100,
                exit_date=calendar[index + 2].date(),
                exit_price=101,
                exit_type="target",
            )
        )
    sleeve_input = CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=prices,
        candidates=tuple(candidates),
        raw_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_signals=tuple(candidate.signal_date for candidate in candidates),
        legacy_candidates=tuple(candidates),
    )
    evidence = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=sleeve_input,
        as_of=calendar[-1].date(),
        completed_through=calendar[-1].date(),
        observed_at=_after_session_close(calendar[-1].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=ExecutionCostPolicy(),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=10,
            exit_slippage_bps=10,
            fee_bps_per_side=1,
        ),
        critical_drift=False,
    )

    activation = evaluate_shadow_activation(
        registration,
        evidence,
        current_definition_fingerprint=registration.definition_fingerprint,
    )

    assert len(evidence.simulated_fills) == 12
    assert evidence.cumulative_return > 0
    assert evidence.stress_cumulative_return > 0
    assert evidence.stress_profit_factor == "Infinity"
    assert activation.eligible
    assert all(gate.passed for gate in activation.gates)
    assert any(gate.name == "stress_cumulative_return" for gate in activation.gates)
    assert any(gate.name == "stress_profit_factor" for gate in activation.gates)
    assert activation.disposition == "activation-eligible"
    assert activation.authorized_for_live_orders is False

    cross_shadow = evaluate_shadow_activation(
        registration,
        replace(evidence, shadow_id="shadow-other"),
        current_definition_fingerprint=registration.definition_fingerprint,
    )
    assert not cross_shadow.eligible
    assert any(gate.name == "shadow_identity" and not gate.passed for gate in cross_shadow.gates)

    low_edge_candidates = tuple(replace(candidate, exit_price=100.1) for candidate in candidates)
    stressed_evidence = build_shadow_evidence(
        registration,
        current_definition_fingerprint="a" * 64,
        sleeve_input=replace(
            sleeve_input,
            candidates=low_edge_candidates,
            legacy_candidates=low_edge_candidates,
        ),
        as_of=calendar[-1].date(),
        completed_through=calendar[-1].date(),
        observed_at=_after_session_close(calendar[-1].date()),
        session_calendar=_SESSION_CALENDAR,
        base_policy=registration.base_cost_policy,
        stress_policy=registration.stress_cost_policy,
        critical_drift=False,
    )
    stressed_activation = evaluate_shadow_activation(
        registration,
        stressed_evidence,
        current_definition_fingerprint=registration.definition_fingerprint,
    )
    assert stressed_evidence.cumulative_return > 0
    assert stressed_evidence.stress_cumulative_return < 0
    assert not stressed_activation.eligible
    assert any(
        gate.name == "stress_cumulative_return" and not gate.passed
        for gate in stressed_activation.gates
    )

    missing_current_definition = evaluate_shadow_activation(
        registration,
        evidence,
        current_definition_fingerprint=None,
    )
    assert not missing_current_definition.eligible
    assert any(
        gate.name == "definition_unchanged" and not gate.passed
        for gate in missing_current_definition.gates
    )
