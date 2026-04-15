"""
INDA-007: Relative Strength Momentum Pullback
(INDA 相對強度動量回調)

策略理念：INDA (印度 ETF) 具有人口紅利、IT 服務產業、改革動能等結構性成長優勢。
當 INDA 相對 EEM (新興市場) 展現超額表現時，代表印度在 EM 中具備獨立動量。
在這種動量優勢下買入短期回調。

參考實驗：EWT-007（RS vs EEM，min 0.42）。
本實驗為 INDA 首次嘗試 RS 動量策略，使用 EEM 作為參考基準。
參數依 INDA 較低日波動（0.97% vs EWT 1.41%）按 ~0.7x 縮放。

Att1: EEM ref, RS>=2%, pullback 1.5-4%, TP+3.5%/SL-4.0%/20d
  → Part A -0.40 (25訊號, WR 36%, -28.49%), Part B -0.08 (7訊號, WR 42.9%, -2.35%)
  → 失敗：RS 2% 門檻太鬆，48% 停損率。INDA 在熊市仍可跑贏 EEM，RS 不代表絕對上漲動量。

Att2: EEM ref, RS>=3%, pullback 2-4%, ATR>1.15, TP+3.5%/SL-4.0%/20d
  → Part A 0.07 (8訊號, WR 62.5%, +1.24%), Part B 0.00 (1訊號, WR 100%, +3.50%)
  → 過度過濾：Part B 僅 1 訊號無統計意義，A/B 比 8:1 極差
  → RS 3% + ATR 1.15 組合太嚴格，INDA 相對 EEM 的 RS 差異天然較小

Att3: EEM ref, RS>=2.5%, pullback 1.5-4%, ATR>1.10, TP+3.5%/SL-4.0%/20d
  → Part A -0.49 (10訊號, WR 40%, -14.09%), Part B 0.00 (4訊號, WR 100%, +14.75%)
  → 極端市場狀態依賴：Part B 2024-2025 牛市 100% WR，Part A 2019-2023 熊市/震盪慘敗
  → 與 Lesson #26（趨勢/動量策略的市場狀態依賴）完全吻合

總結：3 次嘗試均失敗。INDA vs EEM RS 動量不可行。印度結構性優勢（人口紅利、IT）
是持續性而非週期性的，不像台灣半導體（EWT vs EEM）有明確的週期性動量。
RS 訊號在牛市回調時有效（Part B），但在熊市/震盪期完全無法辨別「暫時回調」
與「趨勢反轉」（Part A 6/10 停損或負到期）。
建議新增 cross_asset_lessons: 單一國家 EM ETF（INDA/FXI）RS 動量 vs 廣基 EM 無效。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA007Config(ExperimentConfig):
    """INDA-007 相對強度動量回調策略參數"""

    reference_ticker: str = "EEM"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.025  # INDA - EEM 20日報酬差 >= 2.5%（Att3：折衷）
    pullback_lookback: int = 5
    pullback_min: float = 0.015  # 5日高點回撤 >= 1.5%（Att3：放寬回 Att1）
    pullback_max: float = 0.04  # 5日高點回撤 <= 4%
    cooldown_days: int = 10

    # ATR 波動率過濾（Att3：降低門檻至 1.10）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10


def create_default_config() -> INDA007Config:
    return INDA007Config(
        name="inda_007_rs_momentum",
        experiment_id="INDA-007",
        display_name="INDA Relative Strength Momentum Pullback",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%（INDA 已驗證甜蜜點）
        stop_loss=-0.04,  # -4.0%
        holding_days=20,
    )
