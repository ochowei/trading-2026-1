"""
IWM-005: RSI(2) 極端超賣均值回歸（停損微調）
(IWM RSI(2) Extreme Oversold Mean Reversion - SL Optimization)

延續 IWM-004 的 RSI(2) 進場架構與 TP +4.0%，微調停損：
- SL -4.25%（vs IWM-004 的 -4.5%）：每筆停損減少 0.25% 虧損
- SL -4.0% 太緊（1 筆 Part A 贏家翻轉為停損），-4.25% 是甜蜜點
- WR 不變（66.7%/66.7%），Part A Sharpe +8.6%，Part B Sharpe +10.7%
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM005Config(ExperimentConfig):
    """IWM-005 RSI(2) + 停損微調參數"""

    # RSI(2) 參數（同 IWM-004）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 IWM-004）
    decline_lookback: int = 2
    decline_threshold: float = -0.025  # 2 日跌幅 >= 2.5%

    # 收盤位置過濾（反轉確認，同 IWM-004）
    close_position_threshold: float = 0.4  # >= 40%

    # 冷卻期（同 IWM-004）
    cooldown_days: int = 5


def create_default_config() -> IWM005Config:
    return IWM005Config(
        name="iwm_005_shorter_hold",
        experiment_id="IWM-005",
        display_name="IWM RSI(2) SL Optimized",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（同 IWM-004）
        stop_loss=-0.0425,  # -4.25%（vs IWM-004 的 -4.5%，微調減少停損虧損）
        holding_days=20,  # 20 天（同 IWM-004）
    )
