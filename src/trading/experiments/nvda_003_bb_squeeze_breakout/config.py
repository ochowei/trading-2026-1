"""
NVDA-003: Bollinger Band Squeeze Breakout 配置
NVDA BB Squeeze Breakout Configuration

假說：NVDA 為動量驅動個股（類似 TSLA），波動收縮後的突破往往產生爆發性上漲。
基於 TSLA-005 成功經驗（Sharpe 0.35/0.37），移植至 NVDA（日波動 3.26% vs TSLA 3-4%）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDABBSqueezeConfig(ExperimentConfig):
    """NVDA BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> NVDABBSqueezeConfig:
    """建立預設配置"""
    return NVDABBSqueezeConfig(
        name="nvda_003_bb_squeeze_breakout",
        experiment_id="NVDA-003",
        display_name="NVDA BB Squeeze Breakout",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
