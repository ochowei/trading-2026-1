"""
NVDA-004: BB Squeeze Breakout Optimized 配置
NVDA BB Squeeze Breakout Optimized Configuration

基於 NVDA-003（Sharpe 0.40/0.47），縮短冷卻期以捕捉更多好訊號：
- SL -7%（與 NVDA-003 相同，Att1 驗證 SL -8% 使虧損更大而不救回交易）
- 冷卻期 10 天（vs NVDA-003 的 15 天，Part A 多捕捉 2 個達標訊號）
- SMA(50) 不變（Att3 驗證 SMA(20) 讓通熊市假突破）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDABBSqueezeOptConfig(ExperimentConfig):
    """NVDA BB Squeeze Breakout Optimized 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> NVDABBSqueezeOptConfig:
    """建立預設配置"""
    return NVDABBSqueezeOptConfig(
        name="nvda_004_bb_squeeze_optimized",
        experiment_id="NVDA-004",
        display_name="NVDA BB Squeeze Optimized",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
