"""
DIA-005: RSI(2) 收窄停損均值回歸
(DIA RSI(2) Tighter SL Mean Reversion)

基於 DIA-004 測試收窄停損 SL -3.0%（原 -3.5%），
參考 SPY-005 在相似波動度下 SL -3.0% 的成功經驗。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIARsi2TighterSLConfig(ExperimentConfig):
    """DIA RSI(2) 收窄停損參數"""

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


def create_default_config() -> DIARsi2TighterSLConfig:
    return DIARsi2TighterSLConfig(
        name="dia_005_tighter_sl",
        experiment_id="DIA-005",
        display_name="DIA RSI(2) Tighter SL Mean Reversion",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-004）
        stop_loss=-0.035,  # -3.5%（同 DIA-004）
        holding_days=20,  # 20 天（同 DIA-004）
    )
