from dataclasses import replace

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.experiments.gld_003_trailing_stop.trailing_backtester import (
    TrailingStopBacktester,
)


def execution_config() -> ExperimentConfig:
    return ExperimentConfig(
        name="fixture",
        tickers=["FIX"],
        profit_target=0.10,
        stop_loss=-0.10,
        holding_days=3,
    )


def unfinished_frame() -> pd.DataFrame:
    index = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 103.0, 104.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [100.0, 102.0, 103.0],
            "Volume": [1000, 1000, 1000],
            "Signal": [True, False, False],
        },
        index=index,
    )


def test_execution_backtester_preserves_open_position() -> None:
    result = ExecutionModelBacktester(execution_config(), slippage_pct=0.001).run(
        unfinished_frame(), preserve_open_positions=True
    )
    assert result["trades"] == []
    assert result["open_count"] == 1
    position = result["open_positions"][0]
    assert position["status"] == "open"
    assert position["entry_date"] == "2026-01-06"
    assert position["valuation_date"] == "2026-01-07"
    assert position["mark_price"] == 103.0
    assert position["holding_days"] == 1


def test_execution_backtester_default_remains_backward_compatible() -> None:
    result = ExecutionModelBacktester(execution_config(), slippage_pct=0.001).run(
        unfinished_frame()
    )
    assert "open_positions" not in result
    assert result["trades"][0]["exit_type"] == "time_expiry"


def test_final_day_signal_is_unfilled_not_open() -> None:
    df = unfinished_frame()
    df["Signal"] = [False, False, True]
    result = ExecutionModelBacktester(execution_config()).run(df, preserve_open_positions=True)
    assert result["open_count"] == 0
    assert result["unfilled_count"] == 1


def test_trailing_backtester_reports_current_trailing_state() -> None:
    config = replace(execution_config(), profit_target=0.20)
    result = TrailingStopBacktester(
        config,
        slippage_pct=0.001,
        trail_activation_pct=0.01,
        trail_distance_pct=0.05,
    ).run(unfinished_frame(), preserve_open_positions=True)
    position = result["open_positions"][0]
    assert position["trail_activated"] is True
    assert position["current_stop"] > position["initial_stop"]
