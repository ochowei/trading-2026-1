"""
SIVR 急跌 + RSI(5) 均值回歸配置
(SIVR Sharp Decline + RSI(5) Mean Reversion Config)

與 SIVR-005 不同，改用 RSI(5) 取代 Williams %R，
並加入 2 日跌幅過濾，專注捕捉急速殺跌的投降性賣壓事件。
SL 從 -3.5% 放寬至 -4.5% 以配合 SIVR 的高波動特性。

Differs from SIVR-005 by using RSI(5) instead of Williams %R,
plus a 2-day decline filter to capture sharp capitulation events.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRSharpDeclineRSI5Config(ExperimentConfig):
    """SIVR 急跌 + RSI(5) 均值回歸參數"""

    # 回檔條件（同 SIVR-005 基礎）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    pullback_cap: float = -0.15  # 回檔 ≤15%（過濾極端崩盤）

    # RSI(5) 超賣條件（取代 WR(10)）
    rsi_period: int = 5
    rsi_threshold: float = 30.0  # RSI(5) < 30

    # 2 日跌幅條件（急跌過濾）
    decline_days: int = 2
    decline_threshold: float = -0.035  # 2 日跌幅 ≥ 3.5%

    cooldown_days: int = 10


def create_default_config() -> SIVRSharpDeclineRSI5Config:
    return SIVRSharpDeclineRSI5Config(
        name="sivr_011_sharp_decline_rsi5",
        experiment_id="SIVR-011",
        display_name="SIVR Sharp Decline + RSI(5) Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.045,  # -4.5%（寬 SL，配合 SIVR 波動）
        holding_days=15,
    )
