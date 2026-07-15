import math

import pandas as pd
import pytest

from trading.followup_backtest import (
    DailyEquityPoint,
    StrategyBacktestResult,
    build_portfolio_result,
    compute_equity_metrics,
    simulate_strategy_sleeve,
)


def ledger_frame() -> pd.DataFrame:
    index = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"])
    return pd.DataFrame(
        {
            "Open": [10.0, 10.0, 11.0, 12.0],
            "High": [10.5, 11.0, 12.0, 13.0],
            "Low": [9.5, 9.5, 10.0, 11.0],
            "Close": [10.0, 11.0, 12.0, 12.0],
            "Volume": 1000,
        },
        index=index,
    )


def test_open_position_is_marked_to_market_but_not_counted_as_completed() -> None:
    frame = ledger_frame()
    raw = {
        "trades": [],
        "open_positions": [
            {
                "status": "open",
                "date": "2026-01-05",
                "entry_date": "2026-01-06",
                "entry": 10.0,
                "valuation_date": "2026-01-08",
                "mark_price": 12.0,
                "unrealized_return_pct": 20.0,
            }
        ],
        "unfilled_signals": [],
    }
    trades, points = simulate_strategy_sleeve(tuple(frame.index), frame, raw, 1000.0)
    assert trades[0].status == "open"
    assert trades[0].quantity == 100.0
    assert points[-1].equity == 1200.0


def test_overlapping_signal_is_skipped_without_borrowing() -> None:
    frame = ledger_frame()
    raw = {
        "trades": [
            {
                "date": "2026-01-05",
                "entry_date": "2026-01-06",
                "exit_date": "2026-01-08",
                "entry": 10.0,
                "exit": 12.0,
                "return_pct": 20.0,
                "exit_type": "target",
            },
            {
                "date": "2026-01-06",
                "entry_date": "2026-01-07",
                "exit_date": "2026-01-08",
                "entry": 11.0,
                "exit": 12.0,
                "return_pct": 9.090909,
                "exit_type": "target",
            },
        ],
        "open_positions": [],
        "unfilled_signals": [],
    }
    trades, points = simulate_strategy_sleeve(tuple(frame.index), frame, raw, 1000.0)
    assert [trade.status for trade in trades] == ["completed", "skipped_insufficient_cash"]
    assert points[-1].equity == 1200.0
    assert all(point.cash >= 0 for point in points)


def test_completed_trade_keeps_realized_return_instead_of_last_mtm() -> None:
    frame = ledger_frame()
    frame.loc[pd.Timestamp("2026-01-07"), "Close"] = 10.5
    raw = {
        "trades": [
            {
                "date": "2026-01-05",
                "entry_date": "2026-01-06",
                "exit_date": "2026-01-08",
                "entry": 10.0,
                "exit": 12.0,
                "return_pct": 20.0,
                "exit_type": "target",
            }
        ],
        "open_positions": [],
        "unfilled_signals": [],
    }
    trades, _ = simulate_strategy_sleeve(tuple(frame.index), frame, raw, 1000.0)
    assert trades[0].status == "completed"
    assert trades[0].return_pct == 0.20


def test_known_equity_metrics_include_max_drawdown() -> None:
    metrics = compute_equity_metrics(pd.Series([100.0, 120.0, 90.0, 108.0]))
    assert metrics["total_return"] == 0.08
    assert metrics["max_drawdown"] == -0.25
    assert metrics["final_equity"] == 108.0
    assert math.isfinite(metrics["annualized_volatility"])
    assert math.isfinite(metrics["sharpe_ratio"])


def _point(date: str, equity: float, cash: float, position: float) -> DailyEquityPoint:
    return DailyEquityPoint(
        date=pd.Timestamp(date),
        equity=equity,
        cash=cash,
        position_value=position,
        daily_return=None,
        drawdown=0.0,
        utilization=position / equity if equity else 0.0,
        open_positions=int(position > 0),
    )


def test_portfolio_known_return_and_max_drawdown_keep_failed_sleeve_in_cash() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"]))
    successful = StrategyBacktestResult(
        experiment_name="alpha",
        label="ALPHA",
        ticker="AAA",
        requested_days=3,
        sleeve_initial_cash=500.0,
        daily_equity=[
            _point("2026-01-05", 500.0, 500.0, 0.0),
            _point("2026-01-06", 600.0, 0.0, 600.0),
            _point("2026-01-07", 450.0, 0.0, 450.0),
        ],
    )
    failed = StrategyBacktestResult(
        experiment_name="failed",
        label="FAILED",
        ticker="BAD",
        requested_days=3,
        sleeve_initial_cash=500.0,
        error="download failed",
    )
    result = build_portfolio_result(calendar, [successful, failed], 500.0)
    assert result.initial_equity == 1000.0
    assert result.final_equity == 950.0
    assert result.total_return == -0.05
    assert result.max_drawdown == pytest.approx(-150 / 1100)
    assert result.daily_equity[-1].cash == 500.0
    assert result.maximum_open_positions == 1
