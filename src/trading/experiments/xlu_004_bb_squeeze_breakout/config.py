"""
XLU-004: Bollinger Band Squeeze Breakout 配置
XLU BB Squeeze Breakout Configuration

假說：XLU 公用事業 ETF 在波動收縮後突破時，可產生穩定的動量上漲。
BB Squeeze Breakout 已在多個資產驗證成功（NVDA-004, FCX-004, IWM-006, TSLA-005）。
XLU 日波動 ~1.08%，出場參數按比例縮放（相對 IWM ~1.5-2% 約 0.6x）。

風險：XLU 是防禦性板塊，動量效應可能較弱。COPX-005 驗證 ETF 分散化
可能削弱突破動能，但 XLU 是高流動性 ETF，且公用事業有利率敏感動量效應。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU004BBSqueezeConfig(ExperimentConfig):
    """XLU-004 BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 7


def create_default_config() -> XLU004BBSqueezeConfig:
    """建立預設配置"""
    return XLU004BBSqueezeConfig(
        name="xlu_004_bb_squeeze_breakout",
        experiment_id="XLU-004",
        display_name="XLU BB Squeeze Breakout",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.04,
        holding_days=20,
    )
