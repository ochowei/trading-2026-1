from datetime import date

import pandas as pd
import pytest

from trading.core.sleeve_engine import (
    CandidateTrade,
    CanonicalSleeveEngine,
    ExecutionCostPolicy,
    build_parity_report,
    compute_daily_equity_metrics,
    evaluate_canonical_sleeve,
    evaluate_cost_scenarios,
    serialize_canonical_sleeve_evidence,
)


def test_overlapping_signal_is_skipped_without_increasing_sleeve_exposure() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"]))
    closes = pd.Series([10.0, 11.0, 12.0, 12.0], index=pd.DatetimeIndex(calendar))
    candidates = (
        CandidateTrade(
            signal_date=date(2026, 1, 5),
            entry_date=date(2026, 1, 6),
            entry_price=10.0,
            exit_date=date(2026, 1, 8),
            exit_price=12.0,
            exit_type="target",
        ),
        CandidateTrade(
            signal_date=date(2026, 1, 6),
            entry_date=date(2026, 1, 7),
            entry_price=11.0,
            exit_date=date(2026, 1, 8),
            exit_price=12.0,
            exit_type="target",
        ),
    )

    result = CanonicalSleeveEngine(initial_capital=1000.0).run(
        calendar=calendar,
        close_prices=closes,
        candidates=candidates,
    )

    assert [trade.status for trade in result.trades] == ["completed", "skipped"]
    assert result.trades[0].quantity == 100.0
    assert result.trades[1].reason == "position_already_open"
    assert result.final_equity == 1200.0
    assert max(point.open_positions for point in result.daily_equity) == 1
    assert all(point.cash >= 0 for point in result.daily_equity)


def test_cost_scenarios_apply_preregistered_base_and_stress_costs() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    closes = pd.Series([100.0, 100.0], index=pd.DatetimeIndex(calendar))
    candidates = (
        CandidateTrade(
            signal_date=date(2026, 1, 2),
            entry_date=date(2026, 1, 5),
            entry_price=100.0,
            exit_date=date(2026, 1, 6),
            exit_price=100.0,
            exit_type="time_expiry",
        ),
    )

    scenarios = evaluate_cost_scenarios(
        calendar=calendar,
        close_prices=closes,
        candidates=candidates,
        initial_capital=1000.0,
        base_policy=ExecutionCostPolicy(
            entry_slippage_bps=10.0,
            exit_slippage_bps=10.0,
            fee_bps_per_side=5.0,
        ),
        stress_policy=ExecutionCostPolicy(
            entry_slippage_bps=25.0,
            exit_slippage_bps=25.0,
            fee_bps_per_side=10.0,
        ),
    )

    assert scenarios.gross.final_equity == 1000.0
    assert scenarios.stress_net.final_equity < scenarios.base_net.final_equity < 1000.0
    assert scenarios.base_policy.entry_slippage_bps == 10.0
    assert scenarios.stress_policy.exit_slippage_bps == 25.0


def test_stress_cost_policy_cannot_be_less_adverse_than_base_policy() -> None:
    with pytest.raises(ValueError, match="stress cost policy"):
        evaluate_cost_scenarios(
            calendar=(),
            close_prices=pd.Series(dtype=float),
            candidates=(),
            initial_capital=1.0,
            base_policy=ExecutionCostPolicy(10.0, 10.0, 2.0),
            stress_policy=ExecutionCostPolicy(5.0, 20.0, 2.0),
        )


def test_trade_with_future_exit_stays_open_until_exit_event_is_processed() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    closes = pd.Series([100.0, 105.0], index=pd.DatetimeIndex(calendar))
    candidate = CandidateTrade(
        signal_date=date(2026, 1, 2),
        entry_date=date(2026, 1, 5),
        entry_price=100.0,
        exit_date=date(2026, 1, 7),
        exit_price=110.0,
        exit_type="target",
    )

    result = CanonicalSleeveEngine().run(
        calendar=calendar,
        close_prices=closes,
        candidates=(candidate,),
    )

    assert result.trades[0].status == "open"
    assert result.trades[0].executed_exit_price is None
    assert result.daily_equity[-1].open_positions == 1


def test_daily_equity_metrics_use_the_full_capital_constrained_path() -> None:
    metrics = compute_daily_equity_metrics(
        [1000.0, 1200.0, 900.0, 1080.0],
        initial_equity=1000.0,
    )

    assert metrics.total_return == 0.08
    assert metrics.final_equity == 1080.0
    assert metrics.max_drawdown == -0.25
    assert metrics.annualized_volatility is not None
    assert metrics.sharpe_ratio is not None


def test_empty_daily_equity_path_does_not_invent_annualized_metrics() -> None:
    metrics = compute_daily_equity_metrics([], initial_equity=1.0)

    assert metrics.final_equity == 1.0
    assert metrics.total_return == 0.0
    assert metrics.annualized_return is None
    assert metrics.annualized_volatility is None
    assert metrics.sharpe_ratio is None
    assert metrics.max_drawdown == 0.0


def test_scenario_metrics_include_first_session_cost_drawdown_from_initial_capital() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    closes = pd.Series([100.0, 100.0], index=pd.DatetimeIndex(calendar))
    candidate = CandidateTrade(
        signal_date=date(2026, 1, 2),
        entry_date=date(2026, 1, 5),
        entry_price=100.0,
        exit_date=date(2026, 1, 6),
        exit_price=100.0,
        exit_type="target",
    )
    evaluation = evaluate_canonical_sleeve(
        calendar=calendar,
        close_prices=closes,
        candidates=(candidate,),
        initial_capital=1000.0,
        base_policy=ExecutionCostPolicy(10.0, 10.0, 5.0),
        stress_policy=ExecutionCostPolicy(20.0, 20.0, 10.0),
        legacy_candidates=(candidate,),
    )

    ledger_drawdown = min(point.drawdown for point in evaluation.scenarios.base_net.daily_equity)
    assert evaluation.base_net_metrics.max_drawdown == ledger_drawdown


def test_parity_report_classifies_overlap_as_intentional_trade_difference() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"]))
    closes = pd.Series([10.0, 10.0, 12.0], index=pd.DatetimeIndex(calendar))
    legacy_candidates = (
        CandidateTrade(
            signal_date=date(2026, 1, 2),
            entry_date=date(2026, 1, 5),
            entry_price=10.0,
            exit_date=date(2026, 1, 7),
            exit_price=12.0,
            exit_type="target",
        ),
        CandidateTrade(
            signal_date=date(2026, 1, 5),
            entry_date=date(2026, 1, 6),
            entry_price=10.0,
            exit_date=date(2026, 1, 7),
            exit_price=12.0,
            exit_type="target",
        ),
    )
    canonical = CanonicalSleeveEngine(initial_capital=1000.0).run(
        calendar=calendar,
        close_prices=closes,
        candidates=legacy_candidates,
    )

    report = build_parity_report(
        legacy_candidates=legacy_candidates,
        canonical=canonical,
    )

    assert report.signal_differences == ()
    assert len(report.trade_differences) == 1
    assert report.trade_differences[0].classification == "intentional_policy_difference"
    assert report.trade_differences[0].reason == "position_already_open"
    assert report.has_unclassified_differences is False


def test_parity_report_separates_signal_parity_from_trade_detail_changes() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    closes = pd.Series([100.0, 110.0], index=pd.DatetimeIndex(calendar))
    canonical_candidate = CandidateTrade(
        signal_date=date(2026, 1, 2),
        entry_date=date(2026, 1, 5),
        entry_price=100.0,
        exit_date=date(2026, 1, 6),
        exit_price=110.0,
        exit_type="target",
    )
    legacy_candidate = CandidateTrade(
        signal_date=date(2026, 1, 2),
        entry_date=date(2026, 1, 5),
        entry_price=100.0,
        exit_date=date(2026, 1, 6),
        exit_price=105.0,
        exit_type="target",
    )
    canonical = CanonicalSleeveEngine().run(
        calendar=calendar,
        close_prices=closes,
        candidates=(canonical_candidate,),
    )

    report = build_parity_report(
        legacy_candidates=(legacy_candidate,),
        canonical=canonical,
    )

    assert report.signal_differences == ()
    assert {item.reason for item in report.trade_differences} == {
        "missing_from_canonical_trades",
        "missing_from_legacy_trades",
    }
    assert report.has_unclassified_differences


def test_parity_report_compares_legacy_trades_to_canonical_execution_outcomes() -> None:
    candidate = CandidateTrade(
        signal_date=date(2026, 1, 2),
        entry_date=date(2026, 1, 7),
        entry_price=100.0,
        exit_date=date(2026, 1, 8),
        exit_price=110.0,
        exit_type="target",
    )
    canonical = CanonicalSleeveEngine().run(
        calendar=tuple(pd.to_datetime(["2026-01-05", "2026-01-06"])),
        close_prices=pd.Series(
            [100.0, 100.0],
            index=pd.to_datetime(["2026-01-05", "2026-01-06"]),
        ),
        candidates=(candidate,),
    )

    report = build_parity_report(
        legacy_candidates=(candidate,),
        canonical=canonical,
    )

    assert report.signal_differences == ()
    assert len(report.trade_differences) == 1
    assert report.trade_differences[0].reason == "missing_from_canonical_trades"
    assert report.has_unclassified_differences


def test_canonical_evaluation_keeps_raw_diagnostics_and_ranks_base_net_path() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"]))
    closes = pd.Series([100.0, 105.0, 110.0], index=pd.DatetimeIndex(calendar))
    candidates = (
        CandidateTrade(
            signal_date=date(2026, 1, 2),
            entry_date=date(2026, 1, 5),
            entry_price=100.0,
            exit_date=date(2026, 1, 7),
            exit_price=110.0,
            exit_type="target",
        ),
    )

    evaluation = evaluate_canonical_sleeve(
        calendar=calendar,
        close_prices=closes,
        candidates=candidates,
        initial_capital=1.0,
        base_policy=ExecutionCostPolicy(5.0, 5.0, 1.0),
        stress_policy=ExecutionCostPolicy(20.0, 20.0, 2.0),
        raw_signals=(date(2026, 1, 2), date(2026, 1, 3)),
        legacy_signals=(date(2026, 1, 2), date(2026, 1, 3)),
        legacy_candidates=candidates,
    )

    assert evaluation.raw_candidates == candidates
    assert evaluation.ranking_metrics == evaluation.base_net_metrics
    assert evaluation.gross_metrics.final_equity == 1.1
    assert evaluation.stress_net_metrics.final_equity < evaluation.base_net_metrics.final_equity
    assert evaluation.parity_report.has_unclassified_differences is False
    comparison = evaluation.parity_report.trade_comparisons[0]
    assert comparison.legacy_entry_price == 100.0
    assert comparison.canonical_executed_entry_price > 100.0
    assert comparison.canonical_quantity > 0
    assert comparison.canonical_total_fees > 0
    assert any(
        item.reason == "execution_cost_policy"
        for item in evaluation.parity_report.trade_differences
    )

    evidence = serialize_canonical_sleeve_evidence(evaluation)
    assert evidence["engine_version"] == "canonical-sleeve-v1"
    assert evidence["ranking_scenario"] == "base_net"
    assert evidence["cost_policies"]["base"]["entry_slippage_bps"] == 5.0
    assert evidence["cost_policies"]["stress"]["exit_slippage_bps"] == 20.0
    assert evidence["raw_signals"] == ["2026-01-02", "2026-01-03"]
    assert len(evidence["raw_candidates"]) == 1
    assert evidence["raw_candidates"][0]["signal_date"] == "2026-01-02"
