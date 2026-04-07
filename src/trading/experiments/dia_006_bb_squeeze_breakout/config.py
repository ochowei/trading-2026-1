"""
DIA-006: Bollinger Band Squeeze Breakout 配置
DIA BB Squeeze Breakout Configuration

假說：DIA (道瓊 ETF) 在波動收縮後突破時，藍籌股的動量驅動可產生穩定的趨勢上漲。
BB Squeeze Breakout 已在多資產驗證成功：NVDA-004 (0.50/0.47)、FCX-004 (0.51/0.41)、
IWM-006 (0.31/0.37)、TSLA-005 (0.35/0.37)。
DIA 日波動 ~1.0-1.2%，出場參數按比例縮放（低於 IWM 的 5%/4.5%）。

風險：COPX-005 驗證 ETF 分散化可能削弱突破動能，但 DIA 僅 30 檔藍籌股（vs COPX 礦業），
且道瓊歷史上有機構資金流入驅動的動量特性。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA006BBSqueezeConfig(ExperimentConfig):
    """DIA-006 BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10


def create_default_config() -> DIA006BBSqueezeConfig:
    """建立預設配置"""
    return DIA006BBSqueezeConfig(
        name="dia_006_bb_squeeze_breakout",
        experiment_id="DIA-006",
        display_name="DIA BB Squeeze Breakout",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.035,
        holding_days=20,
    )
