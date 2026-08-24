"""
TSLA-006: Donchian Channel Breakout 配置
TSLA Donchian Channel Breakout Configuration

假說：TSLA 突破 N 日新高（Donchian 上軌），搭配 ATR 收縮過濾，
捕捉波動收斂後的方向性突破。與 TSLA-005 的 BB Squeeze 不同，
使用價格通道而非波動率帶作為突破定義，可能捕捉不同的突破訊號。

Att3: 改用 Donchian Channel + ATR 收縮 + SMA(50) 趨勢。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLATrendPullbackConfig(ExperimentConfig):
    """TSLA Donchian Channel Breakout 策略專屬參數"""

    donchian_period: int = 20
    atr_period: int = 14
    atr_percentile_window: int = 60
    atr_percentile: float = 0.30
    atr_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> TSLATrendPullbackConfig:
    """建立預設配置"""
    return TSLATrendPullbackConfig(
        name="tsla_006_trend_pullback",
        experiment_id="TSLA-006",
        display_name="TSLA Donchian Channel Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
