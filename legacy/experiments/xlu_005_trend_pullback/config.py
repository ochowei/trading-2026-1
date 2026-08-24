"""
XLU-005: Cross-Asset Relative Value 配置
XLU Cross-Asset Relative Value Configuration

假說：XLU（公用事業 ETF）與 TLT（長期國債 ETF）同為利率敏感資產。
當 TLT 上漲（利率下降）但 XLU 尚未跟上時，XLU 預期將補漲。
此策略利用兩者的短期背離作為進場信號。

這是一種配對交易（Pairs Trading）衍生策略，
不同於均值回歸（極端超賣）和突破（波動擴張）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU005Config(ExperimentConfig):
    """XLU-005 Cross-Asset Relative Value 策略專屬參數"""

    tlt_return_lookback: int = 10
    tlt_min_return: float = 0.02
    xlu_max_return: float = 0.005
    rsi_period: int = 14
    rsi_upper: float = 50.0
    sma_long_period: int = 100
    cooldown_days: int = 15


def create_default_config() -> XLU005Config:
    """建立預設配置"""
    return XLU005Config(
        name="xlu_005_trend_pullback",
        experiment_id="XLU-005",
        display_name="XLU Cross-Asset Relative Value",
        tickers=["XLU"],
        data_start="2010-01-01",
        profit_target=0.025,
        stop_loss=-0.04,
        holding_days=20,
    )
