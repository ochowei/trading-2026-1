"""
TSLA-009: BB Wide Band Breakout 配置
TSLA BB Wide Band Breakout Configuration

Att1: BB(20,2.5) 寬帶 — Part A Sharpe 0.22，Part B 僅 3 訊號。寬帶未改善訊號品質。
Att2（最佳）: BB(20,2.0) + 30th百分位擠壓 + 冷卻10天 — Part A 0.40/Part B 0.53，min 0.40（+14.3% vs TSLA-005）。
Att3: BB(20,2.0) + 25th百分位 + 冷卻10天 — Part A 0.35/Part B 0.37（= TSLA-005），冷卻期變更無影響。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLABBWideConfig(ExperimentConfig):
    """TSLA BB Wide Band Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> TSLABBWideConfig:
    """建立預設配置"""
    return TSLABBWideConfig(
        name="tsla_009_bb_wide_breakout",
        experiment_id="TSLA-009",
        display_name="TSLA BB Wide Band Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
