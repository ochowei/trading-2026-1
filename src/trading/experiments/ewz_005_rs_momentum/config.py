"""
EWZ-005: Relative Strength Momentum Pullback
(EWZ 相對強度動量回調)

策略理念：EWZ (巴西 ETF) 大宗商品權重極高 (Vale, Petrobras)，當 EWZ 相對 EEM (新興市場)
展現超額表現時，代表巴西商品週期在 EM 中領先。在這種動量優勢下買入短期回調。

參考實驗：EWT-007（RS vs EEM, min(A,B) 0.42），SOXL-010（RS vs SPY, min(A,B) 0.70）。
EWT vs EEM 有效因半導體週期性；EWZ vs EEM 預期有效因商品週期性。

Att1: EEM ref, RS(20d)>=3%, pullback 3-7%, TP+5%/SL-4%/18d
  → Part A 0.46 (24訊號, WR 66.7%, +56.16%), Part B -0.33 (4訊號, WR 25.0%, -5.03%)
  → A/B 年化訊號比 2.4:1，Part B 嚴重不足（commodity cycle 集中在 2019-2023）
  → Part A 優秀但 Part B 崩潰，RS 3% + 20日回看在 2024-25 產生太少訊號

Att2: EEM ref, RS(15d)>=2%, pullback 2-6%, ATR>1.1, TP+5%/SL-4%/18d
  → Part A -0.00 (17訊號, WR 47.1%, -1.77%), Part B -0.25 (3訊號, WR 33.3%, -3.43%)
  → ATR 過濾在動量策略中反效果（移除好訊號多於壞），不如均值回歸中有效
  → 降低 RS 門檻 + 加 ATR 使兩期均惡化

Att3: EEM ref, RS(10d)>=4%, pullback 2-5%, TP+5%/SL-4%/18d
  → Part A -0.21 (20訊號, WR 35.0%, -18.35%), Part B 0.46 (3訊號, WR 66.7%, +5.73%)
  → A/B 完全反轉（vs Att1），10日 RS 生成大量 Part A 假訊號（8 連虧）
  → RS 動量對 EWZ vs EEM 根本無效：巴西商品優勢為宏觀事件驅動，非週期性

結論：三次迭代均未超越 EWZ-002 Att3（min 0.34）。RS 動量不適合 EWZ：
- 巴西商品優勢受大宗商品價格/BRL 匯率/政治事件驅動，不如台灣半導體週期穩定
- A/B 訊號分佈極不穩定（Att1: 24/4, Att3: 20/3），WR 大幅波動
- ATR 過濾在動量策略中反效果（Att2 最差）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ005Config(ExperimentConfig):
    """EWZ-005 相對強度動量回調策略參數"""

    reference_ticker: str = "EEM"
    sma_trend_period: int = 50
    relative_strength_period: int = 10
    relative_strength_min: float = 0.04  # EWZ - EEM 10日報酬差 >= 4%
    pullback_lookback: int = 5
    pullback_min: float = 0.02  # 5日高點回撤 >= 2%
    pullback_max: float = 0.05  # 5日高點回撤 <= 5%
    cooldown_days: int = 10


def create_default_config() -> EWZ005Config:
    return EWZ005Config(
        name="ewz_005_rs_momentum",
        experiment_id="EWZ-005",
        display_name="EWZ Relative Strength Momentum Pullback",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（EWZ 已驗證甜蜜點）
        stop_loss=-0.040,  # -4.0%（EWZ 已驗證甜蜜點）
        holding_days=18,  # EWZ 已驗證 18d > 15d
    )
