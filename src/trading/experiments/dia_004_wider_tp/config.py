"""
DIA-004: RSI(2) 寬獲利目標均值回歸
(DIA RSI(2) Wider TP Mean Reversion)

基於 DIA-003 測試更寬的獲利目標 TP +3.0%（原 +2.5%），
利用 DIA 均值回歸幅度的上端空間，搭配 SL -3.5% / 20d。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIARsi2WiderTPConfig(ExperimentConfig):
    """DIA RSI(2) 寬獲利目標參數"""

    # RSI(2) 參數（同 DIA-003）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 DIA-003）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 DIA-003）
    close_position_threshold: float = 0.4

    # 冷卻期（同 DIA-003）
    cooldown_days: int = 5


def create_default_config() -> DIARsi2WiderTPConfig:
    return DIARsi2WiderTPConfig(
        name="dia_004_wider_tp",
        experiment_id="DIA-004",
        display_name="DIA RSI(2) Wider TP Mean Reversion",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（DIA-003 為 +2.5%）
        stop_loss=-0.035,  # -3.5%（同 DIA-003）
        holding_days=20,  # 20 天（同 DIA-003）
    )
