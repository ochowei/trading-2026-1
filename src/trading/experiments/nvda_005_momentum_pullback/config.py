"""
NVDA-005: Momentum Pullback 配置
NVDA Momentum Pullback Configuration

趨勢延續動量策略（Attempt 2 最佳版本）
- 20日 ROC >= 15%（近期強勢動量）
- 5日回撤 3-8%（短暫整理，非深度回調）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天

結論：Part B Sharpe 0.74 優異但 Part A 0.36 不及 NVDA-004 的 0.50，
min(A,B) = 0.36 < NVDA-004 的 0.47，未能超越當前最佳。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDAMomentumPullbackConfig(ExperimentConfig):
    """NVDA Momentum Pullback 策略專屬參數"""

    sma_trend_period: int = 50
    roc_period: int = 20
    roc_min: float = 0.15
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.08
    cooldown_days: int = 10


def create_default_config() -> NVDAMomentumPullbackConfig:
    """建立預設配置"""
    return NVDAMomentumPullbackConfig(
        name="nvda_005_momentum_pullback",
        experiment_id="NVDA-005",
        display_name="NVDA Momentum Pullback",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
