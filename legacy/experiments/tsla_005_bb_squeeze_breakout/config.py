"""
TSLA-005: Bollinger Band Squeeze Breakout 配置
TSLA BB Squeeze Breakout Configuration

假說：TSLA 動量驅動，波動收縮後的突破往往產生爆發性上漲。
與 TSLA-001~004 均值回歸策略完全不同，嘗試趨勢跟蹤/突破方向。
Att2: 放寬擠壓為 60 日 25th 百分位 + 5 日內曾發生擠壓即可。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLABBSqueezeConfig(ExperimentConfig):
    """TSLA BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> TSLABBSqueezeConfig:
    """建立預設配置"""
    return TSLABBSqueezeConfig(
        name="tsla_005_bb_squeeze_breakout",
        experiment_id="TSLA-005",
        display_name="TSLA BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
