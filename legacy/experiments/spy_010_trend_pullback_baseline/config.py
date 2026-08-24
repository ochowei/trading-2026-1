"""SPY-010 qualification baseline reproducing SPY-007 Attempt 2.

This is a family comparator, not a new claim that trend pullback improves SPY research
performance. It freezes the documented SMA(20) pullback variant before SPY-007 added the
ClosePos confirmation and extended its cooldown in Attempt 3.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SPY010TrendPullbackBaselineConfig(ExperimentConfig):
    """SPY-010 趨勢回檔 family baseline 參數。"""

    sma_short_period: int = 20
    sma_mid_period: int = 50
    sma_long_period: int = 200
    cooldown_days: int = 10


def create_default_config() -> SPY010TrendPullbackBaselineConfig:
    """建立 SPY-007 Attempt 2 的固定 baseline 設定。"""
    return SPY010TrendPullbackBaselineConfig(
        name="spy_010_trend_pullback_baseline",
        experiment_id="SPY-010",
        display_name="SPY Trend Pullback Family Baseline (Attempt 2)",
        tickers=["SPY"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
