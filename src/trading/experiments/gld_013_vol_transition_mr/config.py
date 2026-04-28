"""
GLD Post-Capitulation Vol-Transition 均值回歸配置 (GLD-013)

動機：VGK-008 Att2（2026-04-22）首度將 2DD floor 方向驗證於已開發歐洲寬基
ETF（VGK 1.12% vol），min(A,B) Sharpe 0.53→2.60（+390%）。VGK-008 明確
列舉「low-vol defensive 類別」為 2DD floor 方向之待測對象。

GLD（SPDR Gold Shares）為 1.12% vol 的大宗商品 ETF，與 VGK 同 vol 帶且同為
防禦型屬性，現為 cross_asset_lessons 的「基線資產」（base case）。現有
GLD-012 Att3（20 日回檔+WR+反轉K線+無追蹤停損）min(A,B) Sharpe 0.48 為
12 次實驗之全域最優——但 GLD 從未測試過「BB 下軌+回檔上限+2DD floor」
混合進場模式，為 VGK-008 跨類別延伸（歐洲寬基→商品 ETF）之首次驗證。

假設：GLD-012 Att3 的 Part A/B 殘餘 SL/到期虧損多半發生於「淺幅慢漂移」
的黃金緩跌期間（如 2022-2023 通膨+升息雙殺期），這些訊號雖觸發 pullback+WR，
但缺乏真正的 capitulation 動能。加入 2DD floor <= -1.5% 過濾器可選擇性排除
這些弱 MR 訊號。

========================================================================
三次迭代結果（2026-04-22，全部失敗，GLD-012 Att3 min 0.48 仍為全域最優）：
========================================================================

Att1（BB+cap-5%+ATR>1.15+2DD<=-1.5%）：
  Part A 1 訊號 +3.00% Sharpe 0.00 / Part B 0 訊號
  失敗：進場組合過嚴，-5% 回檔上限 + ATR 1.15 + 2DD -1.5% 三重深度過濾
  使 GLD 整個歷史僅 1 訊號通過。GLD 低波動 1.12% 下 ATR spike 較溫和，
  1.15 門檻在 VGK 邊際有效但在 GLD 失效。

Att2（放寬：cap-7%+ATR>1.05+2DD<=-1.0%）：
  Part A 8 訊號 WR 75% Sharpe **0.20** / Part B 2 訊號 WR 100% Sharpe 0.00（零方差）
  失敗：Part A Sharpe 0.20 遠低於 GLD-012 的 0.48，含 2 筆 SL -4.10%
  （2021-02-04、2022-09-01）。這些 SL 發生在 GLD 真正的熊市週期中
  （2021 Q1 實質利率上升、2022 Q3 升息加速），2DD -1.0% 門檻無法過濾
  延續性宏觀拋壓。Part B 僅 2 訊號（均達標）樣本不足。

Att3（對齊 VGK/INDA：2DD<=-2.0%）：
  Part A 2 訊號（1 SL -4.10%、1 到期 +0.75%）Sharpe **-0.69** / Part B 1 訊號 +3%
  失敗：2021-02-04 SL 訊號 2DD 深度 > -2.0% 仍通過，反駁「深 2DD = 真 capitulation」假設。
  VGK-008 的成功依賴「SL 集中於 2DD 淺帶 -0.89~-1.68%」結構——GLD 的 SL 可能
  發生於任意 2DD 深度。加嚴 2DD 門檻只壓縮訊號數，未改善品質。

========================================================================
核心失敗根因（擴展 VGK-008 跨類別邊界）：
========================================================================

1. **GLD（商品 ETF）vs VGK（股票寬基 ETF）結構性差異**：
   - VGK：股票 capitulation 具強 mean-reversion 特性（投資者恐慌後補倉）
   - GLD：黃金價格由實質利率、美元、通膨預期驅動，非 capitulation 動力學
   - 2022-2023 黃金熊市不是「恐慌式」而是「結構性 repricing」：FOMC 升息
     使黃金機會成本上升，實質利率正值使黃金缺乏持有動機
2. **2DD floor 過濾器之隱含前提**：2DD 深度 ∝ capitulation 強度。此前提
   在股票寬基 ETF 成立（恐慌下跌 vs 慢漂移），但在商品 ETF 不成立
   （慢 bleed 亦可深 2DD，如 2021-02 Biden 刺激 -> 通膨預期 -> 實質利率
   - 殖利率 -> 黃金連續 6 週跌）
3. **SL 位置分布差異**：VGK SLs 集中 2DD -0.89 ~ -1.68%（窄帶，可用 floor
   一次過濾），GLD SLs 2DD 從淺到深廣泛分布（無清晰 floor 邊界）
4. **ATR 過濾邊界**：GLD 1.12% vol 等同 VGK，但其 ATR spike 更溫和（商品
   vs 股票），ATR>1.15 在 GLD 觸發率極低；ATR>1.05 又失去區分力

跨資產貢獻（負面結果）：
- 擴展 Post-Capitulation Vol-Transition MR 模式有效類別邊界：
  * 已驗證：broad 股票 ETF（EEM 1.17%、VGK 1.12%、EWJ 1.15%）、
    板塊 ETF（CIBR 1.53%）、single-country EM ETF（INDA 0.97%、EWT/EWZ）
  * 失敗（GLD 驗證）：**商品 ETF（commodity ETF）不適用**——macro-driven
    decline 不符 capitulation dynamics
- 提醒設計類似策略時：確認目標資產之下跌特性為「股票式 capitulation」
  而非「宏觀因素 repricing」，前者才能受益於 2DD floor + BB 下軌混合進場
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD013Config(ExperimentConfig):
    """GLD-013 Post-Capitulation Vol-Transition MR 參數"""

    # BB 下軌進場
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離：10 日回檔上限
    # Att1: -5% 太嚴（僅 1 訊號，BB 下軌 + -5% 雙重過深進場）
    # Att2/Att3: 放寬至 -7%（對齊 VGK-008）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40

    # ATR 當日波動率飆升確認
    # Att1: >1.15 太嚴，GLD 1.12% vol 下 ATR spike 較溫和
    # Att2: 放寬至 >1.05（與 XLU 1.0% vol 邊界一致）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # 2 日急跌過濾（2DD floor）
    # Att1: -1.5% → 組合過嚴僅 1 訊號
    # Att2: -1.0%（Part A 8 訊號含 2 筆 SL -4.10%，Sharpe 0.20）
    # Att3: -2.0%（對齊 VGK/INDA，嘗試濾除 2DD 淺的 SL 訊號）
    twoday_return_floor: float = -0.020

    # 冷卻期（對齊 VGK-008）
    cooldown_days: int = 7


def create_default_config() -> GLD013Config:
    return GLD013Config(
        name="gld_013_vol_transition_mr",
        experiment_id="GLD-013",
        display_name="GLD Post-Capitulation Vol-Transition MR",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（對齊 GLD-012）
        stop_loss=-0.040,  # -4.0%（對齊 GLD-012）
        holding_days=20,
    )
