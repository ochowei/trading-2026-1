"""
EWT-007: Relative Strength Momentum Pullback
(EWT 相對強度動量回調)

策略理念：EWT (台灣 ETF) 半導體權重極高 (TSM >20%)，當 EWT 相對 EEM (新興市場)
展現超額表現時，代表台灣半導體產業在 EM 中領先。在這種動量優勢下買入短期回調。

參考實驗：TSM-007/008（RS vs SMH），NVDA-006（RS vs SMH）。
本實驗為 EWT 首次嘗試 RS 動量策略，使用 EEM 作為參考基準。

Att1★: EEM ref, RS>=3%, pullback 2-5%, TP+3.5%/SL-4.0%/20d
  → Part A 0.42 (19訊號, WR 78.9%, +25.99%), Part B 0.93 (7訊號, WR 85.7%, +18.07%)
  → min(A,B) 0.42 ★ 大幅超越 EWT-006 的 0.28（+50%）
  → A/B 年化訊號比 1.09:1（優秀），A/B 累計差距 30.5%

Att2: EEM ref, RS>=4%, pullback 2-5%, TP+3.5%/SL-4.0%/20d（收緊 RS 門檻）
  → Part A 0.40 (13訊號, WR 76.9%, +16.52%), Part B 0.67 (5訊號, WR 80.0%, +10.22%)
  → min(A,B) 0.40 ✗ 低於 Att1，收緊 RS 過濾掉 2 筆 Part B 好訊號（Feb 2024, Jul 2025）

Att3: SMH ref, RS>=3%, pullback 2-5%, TP+3.5%/SL-4.0%/20d（改用半導體板塊參考）
  → Part A 0.12 (5訊號, WR 60.0%, +1.97%), Part B -0.67 (4訊號, WR 25.0%, -8.72%)
  → min(A,B) -0.67 ✗ 完全失敗，EWT vs SMH 的 RS 訊號品質極差

結論：EEM 是 EWT RS 策略的最佳參考基準。台灣在 EM 中的相對表現
（半導體出口+經濟結構）比 EWT vs SMH（非半導體成分稀釋）更具預測力。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT007Config(ExperimentConfig):
    """EWT-007 相對強度動量回調策略參數"""

    reference_ticker: str = "EEM"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.03  # EWT - EEM 20日報酬差 >= 3%
    pullback_lookback: int = 5
    pullback_min: float = 0.02  # 5日高點回撤 >= 2%
    pullback_max: float = 0.05  # 5日高點回撤 <= 5%
    cooldown_days: int = 10


def create_default_config() -> EWT007Config:
    return EWT007Config(
        name="ewt_007_rs_momentum",
        experiment_id="EWT-007",
        display_name="EWT Relative Strength Momentum Pullback",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（EWT 已驗證甜蜜點）
        stop_loss=-0.04,  # -4.0%
        holding_days=20,
    )
