from datetime import date
from io import StringIO

import pandas as pd
import pytest

from trading.cli import build_parser
from trading.followup_backtest import (
    FollowupBacktestResult,
    PortfolioBacktestResult,
    StrategyBacktestResult,
    render_followup_backtest,
)


def test_followup_backtest_defaults_to_126_days() -> None:
    args = build_parser().parse_args(["followup-backtest"])
    assert args.command == "followup-backtest"
    assert args.days == 126


def test_followup_backtest_accepts_180_days() -> None:
    args = build_parser().parse_args(["followup-backtest", "--days", "180"])
    assert args.days == 180


def test_followup_backtest_start_defaults_to_none() -> None:
    args = build_parser().parse_args(["followup-backtest"])
    assert args.start is None


def test_followup_backtest_accepts_iso_start_date() -> None:
    args = build_parser().parse_args(["followup-backtest", "--start", "2025-01-01", "--days", "20"])
    assert args.start == date(2025, 1, 1)
    assert args.days == 20


@pytest.mark.parametrize("value", ["2025/01/01", "20250101", "2025-02-30", "not-a-date"])
def test_followup_backtest_rejects_invalid_start_date(value: str) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--start", value])
    assert exc_info.value.code == 2


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "abc"])
def test_followup_backtest_rejects_non_positive_integer(value: str) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--days", value])
    assert exc_info.value.code == 2


def test_followup_backtest_rejects_missing_days_value() -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--days"])
    assert exc_info.value.code == 2


def test_followup_parser_keeps_existing_followup_command() -> None:
    args = build_parser().parse_args(["followup"])
    assert args.command == "followup"
    assert not hasattr(args, "days")


def _minimal_result(days: int = 126) -> FollowupBacktestResult:
    strategy = StrategyBacktestResult(
        experiment_name="alpha",
        label="ALPHA-001",
        ticker="AAA",
        requested_days=days,
        sleeve_initial_cash=100000.0,
        signal_count=1,
        completed_count=1,
        win_rate=1.0,
        cumulative_return=0.10,
        avg_trade_return=0.10,
        sharpe_ratio=1.5,
        max_drawdown=-0.02,
        final_equity=110000.0,
    )
    portfolio = PortfolioBacktestResult(
        initial_equity=100000.0,
        final_equity=110000.0,
        total_return=0.10,
        annualized_return=0.21,
        annualized_volatility=0.12,
        sharpe_ratio=1.5,
        max_drawdown=-0.02,
        average_utilization=0.40,
        maximum_utilization=1.0,
        maximum_open_positions=1,
        daily_equity=[],
    )
    return FollowupBacktestResult(
        requested_days=days,
        calendar=tuple(pd.to_datetime(["2026-01-05", "2026-01-06"])),
        strategies=[strategy],
        portfolio=portfolio,
    )


def test_renderer_prints_strategy_and_portfolio_metrics() -> None:
    output = StringIO()
    render_followup_backtest(_minimal_result(), output=output)
    text = output.getvalue()
    assert "ALPHA-001" in text
    assert "AAA" in text
    assert "Portfolio total return" in text
    assert "+10.00%" in text
    assert "Final asset value" in text


def test_renderer_prints_requested_start_and_actual_period() -> None:
    result = _minimal_result()
    result.requested_start = pd.Timestamp("2025-01-01")
    output = StringIO()
    render_followup_backtest(result, output=output)
    text = output.getvalue()
    assert "Requested start: 2025-01-01" in text
    assert "Actual period:" in text


def test_cli_dispatch_passes_days_and_start(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(days: int, start: date | None) -> FollowupBacktestResult:
        captured.update(days=days, start=start)
        return _minimal_result(days)

    monkeypatch.setattr("trading.followup_backtest.run_followup_backtest", fake_run)
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    main(["followup-backtest", "--days", "180", "--start", "2025-01-01"])
    assert captured == {"days": 180, "start": date(2025, 1, 1)}


def test_cli_exits_one_when_all_strategies_fail(monkeypatch) -> None:
    failed = FollowupBacktestResult(
        requested_days=126,
        calendar=(),
        strategies=[
            StrategyBacktestResult(
                experiment_name="bad",
                label="BAD",
                ticker="BAD",
                requested_days=126,
                sleeve_initial_cash=100000.0,
                error="Failed to fetch BAD data",
            )
        ],
        portfolio=None,
    )
    monkeypatch.setattr(
        "trading.followup_backtest.run_followup_backtest",
        lambda days, start=None: failed,
    )
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["followup-backtest"])
    assert exc_info.value.code == 1


def test_cli_exits_one_when_all_evaluations_fail_with_cash_portfolio(monkeypatch) -> None:
    failed = _minimal_result()
    failed.strategies = [
        StrategyBacktestResult(
            experiment_name="bad",
            label="BAD",
            ticker="BAD",
            requested_days=126,
            sleeve_initial_cash=100000.0,
            error="evaluation failed",
        )
    ]
    monkeypatch.setattr(
        "trading.followup_backtest.run_followup_backtest",
        lambda days, start=None: failed,
    )
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["followup-backtest"])
    assert exc_info.value.code == 1


def test_cli_exits_one_when_start_is_after_last_completed_session(monkeypatch) -> None:
    unavailable = FollowupBacktestResult(
        requested_days=5,
        calendar=(),
        strategies=[
            StrategyBacktestResult(
                experiment_name="alpha",
                label="ALPHA",
                ticker="AAA",
                requested_days=5,
                sleeve_initial_cash=100000.0,
            )
        ],
        portfolio=None,
        warnings=["Requested start is after the last available completed session"],
        requested_start=pd.Timestamp("2099-01-01"),
    )
    monkeypatch.setattr(
        "trading.followup_backtest.run_followup_backtest",
        lambda days, start=None: unavailable,
    )
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["followup-backtest", "--start", "2099-01-01", "--days", "5"])
    assert exc_info.value.code == 1


def test_existing_followup_dispatch_and_lookback_remain_unchanged(monkeypatch) -> None:
    called = []
    monkeypatch.setattr("trading.followup.run_followup", lambda: called.append(True))
    from trading.cli import main
    from trading.followup import LOOKBACK_TRADING_DAYS

    main(["followup"])
    assert called == [True]
    assert LOOKBACK_TRADING_DAYS == 60
