"""
IWM-006: Bollinger Band Squeeze Breakout 配置
IWM BB Squeeze Breakout Configuration

假說：IWM 小型股 ETF 在波動收縮後突破時，可產生可觀的動量上漲。
BB Squeeze Breakout 已在 TSLA-005 (0.35/0.37)、NVDA-003 (0.40/0.47)、
FCX-004 (0.51/0.41) 驗證成功。IWM 日波動 ~1.5-2%，出場參數按比例縮放。

風險：COPX-005 驗證 ETF 分散化可能削弱突破動能，但 IWM 流動性遠高於 COPX，
且小型股歷史上有顯著動量效應。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM006BBSqueezeConfig(ExperimentConfig):
    """IWM-006 BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> IWM006BBSqueezeConfig:
    """建立預設配置"""
    return IWM006BBSqueezeConfig(
        name="iwm_006_bb_squeeze_breakout",
        experiment_id="IWM-006",
        display_name="IWM BB Squeeze Breakout",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.05,
        stop_loss=-0.045,
        holding_days=20,
    )
