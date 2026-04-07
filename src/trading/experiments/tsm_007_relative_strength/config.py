"""
TSM-007: Relative Strength Momentum Pullback 配置
TSM Relative Strength Momentum Pullback Configuration

相對強度動量策略（Attempt 1 最佳版本）：在 TSM 相對 SMH（半導體 ETF）具備超額表現時，買入短期回調
- TSM 20日報酬 - SMH 20日報酬 >= 5%（TSM 跑贏板塊，顯示個股 alpha）
- 5日高點回撤 3-7%（短暫整理，非深度回調）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天

與 TSM-006 差異：TSM-006 使用絕對動量 ROC(20)>=10%，本策略使用
相對強度（TSM vs SMH），過濾純板塊 beta 上漲、聚焦 TSM 特有 alpha。

三次嘗試結果：
- Att1: RS >= 5%, pullback 3-7% → Part A 0.64/Part B 1.32, min(A,B) 0.64, 12/10 signals（最佳）
- Att2: RS >= 8%, pullback 3-7% → Part A -0.01/Part B 0.35, min(A,B) -0.01, 8/3 signals（過嚴）
- Att3: RS >= 3%, pullback 3-7% → Part A 0.56/Part B 0.44, min(A,B) 0.44, 19/13 signals（過鬆）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMRelativeStrengthConfig(ExperimentConfig):
    """TSM Relative Strength Momentum Pullback 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10


def create_default_config() -> TSMRelativeStrengthConfig:
    return TSMRelativeStrengthConfig(
        name="tsm_007_relative_strength",
        experiment_id="TSM-007",
        display_name="TSM Relative Strength Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.07,
        holding_days=20,
    )
