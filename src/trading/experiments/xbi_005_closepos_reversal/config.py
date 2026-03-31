"""
XBI-005: 回檔 + Williams %R + 反轉K線均值回歸配置
(XBI Pullback + Williams %R + Reversal Candlestick Config)

在 XBI-001 基礎上加入 ClosePos >= 40% 反轉K線確認。
IWM-005 驗證 ClosePos 在中低波動 ETF 上是必要品質過濾器。
XBI 日波動 ~2.0% 與 IWM (~1.5-2%) 接近，有合理機會有效。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI005Config(ExperimentConfig):
    """XBI-005 回檔 + Williams %R + 反轉K線參數"""

    # 進場指標（同 XBI-001）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80

    # 新增：反轉K線確認
    close_position_threshold: float = 0.35  # ClosePos >= 35%

    cooldown_days: int = 10


def create_default_config() -> XBI005Config:
    return XBI005Config(
        name="xbi_005_closepos_reversal",
        experiment_id="XBI-005",
        display_name="XBI Pullback + WR + Reversal Candlestick",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.050,  # -5.0%
        holding_days=15,  # 15 天
    )
