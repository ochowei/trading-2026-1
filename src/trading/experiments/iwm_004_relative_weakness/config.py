"""
IWM-004: RSI(2) 極端超賣均值回歸（TP +4.0% 測試）
(IWM RSI(2) Extreme Oversold Mean Reversion - TP +4.0% Test)

延續 IWM-003 的 RSI(2) 進場架構，測試更高的獲利目標：
- TP +4.0%（IWM 波動度 1.5-2% 高於 SPY，測試是否可支撐更高 TP）
- SL -4.5% / 20天（維持 IWM-003 已驗證出場）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM004Config(ExperimentConfig):
    """IWM-004 RSI(2) + TP +4.0% 參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # >= 40%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> IWM004Config:
    return IWM004Config(
        name="iwm_004_relative_weakness",
        experiment_id="IWM-004",
        display_name="IWM RSI(2) + TP 4.0%",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（甜蜜點：所有贏利交易仍可達標）
        stop_loss=-0.045,  # -4.5%（維持已驗證值）
        holding_days=20,  # 20 天
    )
