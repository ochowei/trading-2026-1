"""
DIA-005: RSI(2) 延長持倉均值回歸
(DIA RSI(2) Extended Holding Mean Reversion)

同 DIA-004 進場條件與出場參數，僅延長持倉期至 25 天，
讓接近達標的到期交易有更多時間觸及 TP +3.0%。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIAExtendedHoldConfig(ExperimentConfig):
    """DIA RSI(2) 延長持倉參數"""

    # RSI(2) 參數（同 DIA-004）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 DIA-004）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 DIA-004）
    close_position_threshold: float = 0.4

    # 冷卻期（同 DIA-004）
    cooldown_days: int = 5


def create_default_config() -> DIAExtendedHoldConfig:
    return DIAExtendedHoldConfig(
        name="dia_005_extreme_entry",
        experiment_id="DIA-005",
        display_name="DIA RSI(2) Extended Holding Mean Reversion",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-004）
        stop_loss=-0.035,  # -3.5%（同 DIA-004）
        holding_days=25,  # 25 天（DIA-004 為 20 天）
    )
