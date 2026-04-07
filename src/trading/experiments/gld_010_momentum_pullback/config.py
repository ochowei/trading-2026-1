"""
GLD-010: 動量回檔策略 (Momentum Pullback Strategy)

GLD 未嘗試過的策略類型：動量策略。
利用 GLD 的趨勢持續性特性，在強勢動量中買入短期回檔。

三次嘗試記錄：
- Att1: ROC(20)>3% + 5日回檔≥1.5% + SMA(50) + trailing stop, TP+3.0%/SL-3.0%
  → Part A Sharpe 0.00 / Part B 0.36（trailing stop 截斷贏利至+0.6~1.3%，SL-3.0%太緊）
- Att2: ROC(20)>5% + 5日回檔≥1.5% + SMA(50) + trailing stop, TP+3.0%/SL-4.0%
  → Part A Sharpe 0.22 / Part B 0.50（A/B比1.15:1極佳，但trailing stop仍截斷贏利）
- Att3: ROC(20)>5% + 5日回檔≥1.5% + SMA(50)，無trailing stop，TP+3.5%/SL-4.0%/25d
  → Part A Sharpe 0.38 / Part B 0.84（**最佳嘗試**，A/B比1.15:1極佳，但min(A,B)=0.38 < GLD-008的0.45）

結論：動量回檔策略未超越 GLD-008（min 0.38 vs 0.45），但提供有價值發現：
- 移除 trailing stop 大幅改善（Att2 0.22 → Att3 0.38），因動量進場後續走勢需更多空間
- ROC(20)>5% 比 >3% 更有效（Att1 Part A 0.00 → Att2 0.22）
- A/B 平衡極佳（1.15:1），但 Part A 訊號品質不如均值回歸的極端超賣進場
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD010Config(ExperimentConfig):
    """GLD 動量回檔參數"""

    # 動量指標
    roc_period: int = 20  # ROC 回看天數
    roc_threshold: float = 0.05  # ROC > 5%（20日漲幅超過5%，更強動量要求）

    # 短期回檔
    pullback_lookback: int = 5  # 5日回看
    pullback_threshold: float = -0.015  # 從5日高點回檔 ≥1.5%

    # 趨勢確認
    sma_period: int = 50  # SMA(50)
    cooldown_days: int = 7

    # 無追蹤停損（Att3：動量回檔不適合追蹤停損，截斷贏利）


def create_default_config() -> GLD010Config:
    return GLD010Config(
        name="gld_010_momentum_pullback",
        experiment_id="GLD-010",
        display_name="GLD Momentum Pullback",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（無追蹤停損，給動量更多空間）
        stop_loss=-0.040,  # -4.0%（GLD 已驗證甜蜜點）
        holding_days=25,  # 延長持倉，讓動量趨勢發揮
    )
