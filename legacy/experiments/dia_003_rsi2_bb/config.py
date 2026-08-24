"""
DIA-003: RSI(2) 非對稱出場均值回歸
(DIA RSI(2) Asymmetric Exit Mean Reversion)

基於 DIA-002 改進出場參數。
DIA-002 的 5 筆停損均在 1-4 日內觸發，嘗試放寬停損至 -3.5% + 延長持倉至 20 日，
給予交易更多恢復空間。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIARsi2AsymConfig(ExperimentConfig):
    """DIA RSI(2) 非對稱出場參數"""

    # RSI(2) 參數（同 DIA-002）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 DIA-002）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 DIA-002）
    close_position_threshold: float = 0.4

    # 冷卻期（同 DIA-002）
    cooldown_days: int = 5


def create_default_config() -> DIARsi2AsymConfig:
    return DIARsi2AsymConfig(
        name="dia_003_rsi2_bb",
        experiment_id="DIA-003",
        display_name="DIA RSI(2) Asymmetric Exit Mean Reversion",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（同 DIA-002）
        stop_loss=-0.035,  # -3.5%（放寬 1pp）
        holding_days=20,  # 20 天（延長 5 天）
    )
