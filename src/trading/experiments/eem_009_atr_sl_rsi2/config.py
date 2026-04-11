"""
EEM-009: ATR 波動率自適應 RSI(2) + 寬 SL 均值回歸
(EEM ATR Volatility-Adaptive RSI(2) + Wide SL Mean Reversion)

基於 EEM-001 RSI(2) 架構，新增 ATR(5)/ATR(20) 波動率飆升過濾：
- ATR > 1.15 過濾慢磨下跌，只保留急跌恐慌訊號
- SL 從 -3.0% 放寬至 -3.5%，減少 Part A 過多停損
- EEM 日波動 1.17% 在 ATR 過濾有效範圍內（≤ 2.25%）
- 參考 XLU-011（1.0%, ATR>1.15, +272%）和 IWM-011（1.5-2%, ATR>1.1, +67.7%）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM009Config(ExperimentConfig):
    """EEM-009 ATR 波動率自適應 RSI(2) + 寬 SL 參數"""

    # RSI(2) 參數（同 EEM-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0

    # 2 日累計跌幅過濾（同 EEM-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015

    # 收盤位置過濾（同 EEM-001）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（同 EEM-001）
    cooldown_days: int = 5


def create_default_config() -> EEM009Config:
    return EEM009Config(
        name="eem_009_atr_sl_rsi2",
        experiment_id="EEM-009",
        display_name="EEM ATR + Wide SL RSI(2)",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=20,
    )
