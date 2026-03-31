"""
IWM-005: RSI(2) 極端超賣均值回歸（收盤位置優化）
(IWM RSI(2) Extreme Oversold Mean Reversion - Close Position Optimization)

延續 IWM-004 的 RSI(2) 進場架構，收緊收盤位置門檻：
- ClosePos ≥ 50%（從 40% 收緊，要求更強的日內反轉）
- TP +4.0% / SL -4.5% / 20天（維持 IWM-004 出場參數）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM005Config(ExperimentConfig):
    """IWM-005 RSI(2) + ClosePos ≥ 50% 參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.5  # >= 50%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> IWM005Config:
    return IWM005Config(
        name="iwm_005_short_holding",
        experiment_id="IWM-005",
        display_name="IWM RSI(2) + ClosePos 50%",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（維持 IWM-004 甜蜜點）
        stop_loss=-0.045,  # -4.5%（維持已驗證值）
        holding_days=20,  # 20 天
    )
