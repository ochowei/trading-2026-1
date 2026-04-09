"""
IWM-011: Volatility-Adaptive RSI(2) Mean Reversion
(IWM 波動率自適應 RSI(2) 均值回歸)

基於 IWM-005 的 RSI(2) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾：
- ATR > 1.1 是甜蜜點：移除 Part A 3 個停損/到期 + Part B 1 個停損，保留大部分贏家
- ATR > 1.15 / 1.2 太嚴：額外移除 2 個好訊號（2019-10、2022-09），Part A Sharpe 0.52→0.34

Att1: ATR > 1.2 → Part A 0.34 / Part B 0.31, min 0.31（同 IWM-005，無改善）
Att2: ATR > 1.1 → Part A 0.52 / Part B 0.53, min 0.52（+67.7% vs IWM-005）★
Att3: ATR > 1.15 → Part A 0.34 / Part B 0.53, min 0.34（與 1.2 相同 Part A）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM011Config(ExperimentConfig):
    """IWM-011 波動率自適應 RSI(2) 均值回歸參數"""

    # RSI(2) 參數（同 IWM-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 IWM-005）
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（反轉確認，同 IWM-005）
    close_position_threshold: float = 0.4  # >= 40%

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1  # 甜蜜點（1.15/1.2 移除好訊號，< 1.1 未測試）

    # 冷卻期（同 IWM-005）
    cooldown_days: int = 5


def create_default_config() -> IWM011Config:
    return IWM011Config(
        name="iwm_011_vol_adaptive_rsi2",
        experiment_id="IWM-011",
        display_name="IWM Volatility-Adaptive RSI(2)",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（同 IWM-005）
        stop_loss=-0.0425,  # -4.25%（同 IWM-005 甜蜜點）
        holding_days=20,  # 20 天（同 IWM-005）
    )
