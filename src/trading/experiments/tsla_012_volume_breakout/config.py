"""
TSLA-012: Volume-Confirmed BB Squeeze Breakout 配置
TSLA Volume-Confirmed BB Squeeze Breakout Configuration

Att1: Volume > 1.3x 20日均量 — Part A Sharpe 0.22（vs 0.40 基線），移除好訊號多於壞訊號。
Att2（預設）: 延長擠壓持續（7日內≥3日擠壓）— Part A 0.35/Part B 0.37，A/B gap 0.02（最佳平衡）。
Att3: SMA(100) 長期趨勢 — Part A 0.35/Part B 0.17，讓通早期假訊號，惡化 Part B。
三次嘗試均未超越 TSLA-009 Att2（min 0.40），確認 TSLA BB Squeeze Breakout 已達全域最優。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLAVolumeBreakoutConfig(ExperimentConfig):
    """TSLA Volume-Confirmed BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 7
    bb_squeeze_min_days: int = 3
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> TSLAVolumeBreakoutConfig:
    """建立預設配置"""
    return TSLAVolumeBreakoutConfig(
        name="tsla_012_volume_breakout",
        experiment_id="TSLA-012",
        display_name="TSLA Volume-Confirmed BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
