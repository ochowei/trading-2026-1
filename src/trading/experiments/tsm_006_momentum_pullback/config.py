"""
TSM-006: Momentum Pullback 配置
TSM Momentum Pullback Configuration

趨勢延續動量策略（Attempt 3 最佳版本）：在上升趨勢中買入短期回調
- 20日 ROC >= 10%（適中動量門檻）
- 5日高點回撤 3-7%（短暫整理，非深度回調）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天

參考 NVDA-005 架構，針對 TSM 特性調整：
- TSM 日波動 ~2.5%（vs NVDA ~3%），ROC 門檻較低（10% vs 15%）
- 使用成交模型（隔日開盤市價進場）

三次嘗試結果：
- Att1: ROC 12%, pullback 3-8% → min(A,B) Sharpe 0.43, A/B ratio 1.7:1
- Att2: ROC 15%, pullback 3-10% → min(A,B) Sharpe 0.20, A/B ratio 2.2:1（過嚴）
- Att3: ROC 10%, pullback 3-7% → min(A,B) Sharpe 0.46, A/B ratio 1.2:1（最佳）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMMomentumPullbackConfig(ExperimentConfig):
    """TSM Momentum Pullback 策略專屬參數"""

    sma_trend_period: int = 50
    roc_period: int = 20
    roc_min: float = 0.10
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10


def create_default_config() -> TSMMomentumPullbackConfig:
    return TSMMomentumPullbackConfig(
        name="tsm_006_momentum_pullback",
        experiment_id="TSM-006",
        display_name="TSM Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.07,
        holding_days=20,
    )
