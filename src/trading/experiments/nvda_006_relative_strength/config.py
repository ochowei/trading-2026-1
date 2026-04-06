"""
NVDA-006: Relative Strength Momentum Pullback 配置
NVDA Relative Strength Momentum Pullback Configuration

靈感來自 TSM-007 的成功（Sharpe 0.64/1.32）：在個股相對板塊 ETF
展現超額表現時買入回調，捕捉個股 alpha 而非板塊 beta。

策略邏輯（Attempt 1 最佳版本）：
- NVDA 20日報酬 - SMH 20日報酬 >= 5%（NVDA 跑贏板塊）
- 5日高點回撤 3-8%（短暫整理，NVDA 日波動 3.26% 比 TSM 高，放寬上限）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 天（NVDA-004 已驗證 10 天優於 15 天）

出場參數沿用 NVDA 已驗證的甜蜜點：
- TP +8%（硬上限，lesson #45）
- SL -7%（底線，lesson #74）
- 持倉 20 天

三次嘗試結果：
- Att1: RS >= 5%, pullback 3-8% → Part A 0.47/Part B 0.64, min(A,B) 0.47, 35/12 signals（最佳）
- Att2: RS >= 5%, pullback 4-8% → Part A 0.41/Part B 0.34, min(A,B) 0.34（過濾好訊號）
- Att3: RS >= 7%, pullback 3-8% → Part A 0.45/Part B 0.29, min(A,B) 0.29（過嚴）

vs NVDA-004（current best）: Part A 0.50/Part B 0.47, min(A,B) 0.47
RS 策略 min(A,B) 持平，但 Part B OOS Sharpe +36%（0.64 vs 0.47），
A/B 年化訊號比 1.17:1（極佳平衡）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDARelativeStrengthConfig(ExperimentConfig):
    """NVDA Relative Strength Momentum Pullback 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.08
    cooldown_days: int = 10


def create_default_config() -> NVDARelativeStrengthConfig:
    return NVDARelativeStrengthConfig(
        name="nvda_006_relative_strength",
        experiment_id="NVDA-006",
        display_name="NVDA Relative Strength Momentum Pullback",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
