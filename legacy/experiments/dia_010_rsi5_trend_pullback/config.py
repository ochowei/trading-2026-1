"""
DIA-010: RSI(5) 趨勢回調策略
(DIA RSI(5) Trend Pullback Strategy)

在確認的上升趨勢中（Close > SMA(50)），等待 RSI(5) 短期超賣 + 3日幅度回調後進場。
與 DIA-007（SMA proximity 回測）不同：使用 RSI(5) + 3日跌幅捕捉短期超賣。
與 DIA-001~005（RSI(2) 極端超賣均值回歸）不同：加入趨勢過濾，不買熊市深跌。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIARsi5TrendPullbackConfig(ExperimentConfig):
    """DIA RSI(5) 趨勢回調參數"""

    # 趨勢確認：收盤 > SMA(N)
    trend_sma_period: int = 50

    # 回調條件：RSI(5) 超賣
    rsi_period: int = 5
    rsi_threshold: float = 30.0  # RSI(5) < 30

    # 回調幅度：3 日跌幅
    decline_lookback: int = 3
    decline_threshold: float = -0.02  # 3 日跌幅 >= 2%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> DIARsi5TrendPullbackConfig:
    return DIARsi5TrendPullbackConfig(
        name="dia_010_rsi5_trend_pullback",
        experiment_id="DIA-010",
        display_name="DIA RSI(5) Trend Pullback Strategy",
        tickers=["DIA"],
        data_start="2018-01-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.030,  # -3.0%
        holding_days=15,  # 15 天
    )
