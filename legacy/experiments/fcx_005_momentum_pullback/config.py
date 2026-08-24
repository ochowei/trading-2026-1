"""
FCX-005: RSI(2) 短期極端超賣均值回歸 配置
FCX RSI(2) Short-Term Extreme Oversold Mean Reversion Configuration

假說：FCX 日波動 2-4%，RSI(2) 能捕捉 2 日內的極端超賣狀態。
不同於 FCX-001 的 60 日慢速深谷抄底，本策略聚焦非常短期（2日）的劇跌反彈。
基於 SPY-005/DIA-004 的 RSI(2) 架構，按 FCX 波動度縮放出場參數。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCXRSI2Config(ExperimentConfig):
    """FCX RSI(2) 策略專屬參數"""

    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_days: int = 2
    decline_threshold: float = -0.04
    cooldown_days: int = 10


def create_default_config() -> FCXRSI2Config:
    """建立預設配置"""
    return FCXRSI2Config(
        name="fcx_005_momentum_pullback",
        experiment_id="FCX-005",
        display_name="FCX RSI(2) Short-Term Mean Reversion",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
