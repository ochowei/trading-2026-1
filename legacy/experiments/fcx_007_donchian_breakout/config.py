"""
FCX-007: Donchian Channel Breakout 配置
FCX Donchian Channel Breakout Configuration

假說：結合 Donchian 價格突破與波動收縮過濾，捕捉 FCX 在整理期後的趨勢啟動。
Donchian(30) 提供不同於 BB Upper Band 的突破判定（基於實際價格高點），
BB Squeeze 過濾確保只在波動收縮後才進場，避免追漲。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXDonchianConfig(ExperimentConfig):
    """FCX Donchian Breakout 策略專屬參數"""

    donchian_period: int = 30
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> FCXDonchianConfig:
    """建立預設配置"""
    return FCXDonchianConfig(
        name="fcx_007_donchian_breakout",
        experiment_id="FCX-007",
        display_name="FCX Donchian Channel Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
