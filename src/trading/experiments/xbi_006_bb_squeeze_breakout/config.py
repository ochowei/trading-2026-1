"""
XBI-006: Bollinger Band Squeeze Breakout 配置
(XBI BB Squeeze Breakout Configuration)

假說：XBI 生技 ETF 日波動 ~2.0%，與 IWM (~1.5-2%) 接近。
突破策略在類似波動度資產上已成功（NVDA-003, TSLA-005, IWM-006）。
生技板塊有動量驅動特性（FDA 催化劑、板塊輪動），波動收縮後的突破可能優於均值回歸。
參數以 IWM-006（TP+5%/SL-4.5%/20d）為基準，SL 採用 XBI 已驗證的 -5.0% 底線。

結果：三次嘗試均未超越 XBI-005。突破策略在 XBI（分散化 ETF）上無效，
類似 COPX-005 發現。已確認 XBI-005 為全域最優。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI006Config(ExperimentConfig):
    """XBI BB Squeeze Breakout 策略專屬參數"""

    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 15


def create_default_config() -> XBI006Config:
    """建立預設配置"""
    return XBI006Config(
        name="xbi_006_bb_squeeze_breakout",
        experiment_id="XBI-006",
        display_name="XBI BB Squeeze Breakout",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.05,  # +5.0%
        stop_loss=-0.05,  # -5.0% (XBI verified floor)
        holding_days=20,  # 20 天
    )
