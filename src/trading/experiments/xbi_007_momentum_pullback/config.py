"""
XBI-007: Momentum Pullback 配置
XBI Momentum Pullback Configuration

動量回調策略：在上升趨勢中買入短期回調（Attempt 3 最佳版本）
- 20日 ROC >= 8%（動量門檻）
- 5日高點回撤 3.5-6%（適中深度）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天

參考 TSM-006 架構，針對 XBI 特性調整：
- XBI 日波動 ~2.0%（vs TSM ~2.5%），參數縮放 ~0.8x
- 使用成交模型（隔日開盤市價進場）

三次嘗試結果（均未超越 XBI-005 均值回歸 min(A,B) Sharpe 0.36）：
- Att1: ROC 8%, pullback 2.5-5%, TP+5%/SL-5% → Part A -0.01, Part B -0.23
- Att2: ROC 12%, pullback 3-7%, TP+6%/SL-5% → Part A 0.34, Part B 僅 2 訊號
- Att3: ROC 8%, pullback 3.5-6%, TP+4%/SL-5% → Part A 0.02, Part B 0.44（最佳）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBIMomentumPullbackConfig(ExperimentConfig):
    """XBI Momentum Pullback 策略專屬參數"""

    sma_trend_period: int = 50
    roc_period: int = 20
    roc_min: float = 0.08
    pullback_lookback: int = 5
    pullback_min: float = 0.035
    pullback_max: float = 0.06
    cooldown_days: int = 10


def create_default_config() -> XBIMomentumPullbackConfig:
    return XBIMomentumPullbackConfig(
        name="xbi_007_momentum_pullback",
        experiment_id="XBI-007",
        display_name="XBI Momentum Pullback",
        tickers=["XBI"],
        data_start="2018-01-01",
        profit_target=0.04,
        stop_loss=-0.05,
        holding_days=20,
    )
