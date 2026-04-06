"""
FCX-004: Bollinger Band Squeeze Breakout 配置
FCX BB Squeeze Breakout Configuration

假說：FCX 為銅礦龍頭股，銅價趨勢驅動下波動收縮後的突破往往產生爆發性上漲。
基於 TSLA-005/NVDA-003 成功經驗（日波動 3-4%），移植至 FCX（日波動 2-4%）。
FCX-001~003 均為均值回歸策略，本實驗首次嘗試突破方向。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXBBSqueezeConfig(ExperimentConfig):
    """FCX BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> FCXBBSqueezeConfig:
    """建立預設配置"""
    return FCXBBSqueezeConfig(
        name="fcx_004_bb_squeeze_breakout",
        experiment_id="FCX-004",
        display_name="FCX BB Squeeze Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
