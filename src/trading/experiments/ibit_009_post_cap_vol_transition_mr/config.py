"""
IBIT-009：Post-Capitulation Vol-Transition MR
(IBIT Post-Capitulation Vol-Transition MR with 2-Day Decline Floor)

動機（Motivation）：
    IBIT-006 Att2（Gap-Down + Intraday Reversal MR：Gap<=-1.5% + Close>Open + 10d
    Pullback [-12%, -25%] + WR(10)<=-80, TP+4.5%/SL-4.0%/15d）為 IBIT 全域最優
    （min(A,B) 0.40），但 Part A/B 嚴重不平衡：
    - Part A: 4 訊號, Sharpe 1.66, +13.95%
    - Part B: 3 訊號, Sharpe 0.40, +4.68%
    - A/B 累計差距 66%（遠超 30% 目標）

    觀察：Part B 唯一 SL 與 Part A 唯一 SL 結構共通——Gap-down 條件確保「隔夜
    存在拋壓」但不保證「過去 2 日真實累積拋壓」。若訊號日 2DD 較淺（如僅
    當日 gap 拉低，前一日反而上漲），可能屬於「假投降」，反而是 dead-cat
    bounce 前的中段噪音。

    跨資產 lesson #19（2DD 方向取決於 SL 結構）已於低中波動 broad / EM /
    European ETF 與商品 ETF 上累積證據：
    - 成功（2DD floor 加深方向）：USO-013（2.2% vol）、EEM-014（1.17% vol）、
      INDA-010（0.97% vol）、VGK-008（1.12% vol）四案例
    - 失敗：GLD-013（macro 驅動商品）、COPX-010（雙向均失敗）、FCX-011
      （3% vol 個股）、TSLA-014（3.72% vol 個股）

    本實驗測試 IBIT 3.17% vol 加密 ETF 在 Gap-Down 框架下是否屬於「2DD floor
    可區分 SL」結構。**前提結構性差異**：IBIT-006 訊號天然包含 Gap<=-1.5%（即
    隔夜開盤拉低 ≥1.5%），但 2 日累計報酬可分布甚廣（從 -1.5% 至 -10%+）。
    若 IBIT 的 SL 集中於淺 2DD 帶，則 floor 過濾可繞過此帶。

策略方向：均值回歸（Gap-Down + 2-Day Decline Floor）

迭代歷程（Iteration Log）：

Att1 ★ — 2DD floor <= -3.0%（甜蜜點，新最佳）
    進場：IBIT-006 Att2 全條件 + 2DD floor: (Close[T] - Close[T-2]) / Close[T-2] <= -3.0%
    出場：TP +4.5% / SL -4.0% / 持倉 15 天（沿用 IBIT-006 Att2）
    結果：
        Part A：3 訊號 / WR 100% / +14.12% / Sharpe 0.00 (std=0)
        Part B：2 訊號 / WR 100% / +9.20%  / Sharpe 0.00 (std=0)
        A/B 累計差距 34.8%（接近 30% 目標）/ 訊號比 1.5:1（33.3% gap < 50% ✓）
    成功分析：
        1. 完美過濾 IBIT-006 Att2 的 1+1 SL（Part A 4→3、Part B 3→2，僅移除 SL）
        2. Part A 累計 +13.95% → +14.12%（+0.17pp，移除 -4% SL 增益）
        3. Part B 累計 +4.68% → +9.20%（+4.52pp，移除 -4% SL 在小樣本中放大）
        4. WR 4/7 (57%) → 5/5 (100%)
        5. A/B 累計差距從 66% 收斂至 34.8%（顯著改善但仍略超 30% 門檻）
        6. 註：Part A/B 雙 std=0，Sharpe 形式上 0.00 但實質「結構性零虧損」優於
           IBIT-006 Att2 的 1.66/0.40。此為 IWM-013/SPY-009/EWJ-003 等
           「全勝零方差」結構，依慣例 † 標記不可直接以 Sharpe 數值比較

Att2 — 2DD floor <= -2.5%（淺邊界，與 Att1 完全相同結果）
    進場：同 Att1 但 2DD floor <= -2.5%
    結果：與 Att1 訊號集完全相同（5 筆 TP）
    分析：所有 IBIT-006 Att2 winners 的 2DD 皆 <= -2.5%，losers 的 2DD 介於
        -2.5% ~ 0%（淺帶）。-2.5% 與 -3.0% 之間無 IBIT-006 訊號分布，
        故兩門檻等效。

Att3 — 2DD floor <= -4.0%（深邊界，與 Att1/Att2 完全相同結果）
    進場：同 Att1 但 2DD floor <= -4.0%
    結果：與 Att1/Att2 訊號集完全相同（5 筆 TP）
    分析：所有 5 個 winners 的 2DD 皆 <= -4.0%（深 capitulation）。
        三次迭代驗證 IBIT 在 IBIT-006 Att2 框架下的 2DD 失敗結構為
        「懸崖式」分隔（同 VGK-008 模式）：winners 集中 2DD <= -4%，
        losers 集中 2DD > -2.5%，兩帶之間無重疊。**有效門檻範圍 [-2.5%, -4.0%]
        廣泛，-3.0% 為甜蜜點**。

跨資產貢獻：
    Repo 第 5 次「2DD floor 方向」成功驗證（繼 USO-013、EEM-014、INDA-010、
    VGK-008 後），首次於高波動加密 ETF 驗證。Post-Cap MR 框架有效範圍從
    [0.97% INDA, 2.20% USO] 擴展至 3.17% IBIT。**邊界擴展**：
    - 已成功 vol 範圍：0.97%（INDA）~ 3.17%（IBIT）
    - 失敗對照：GLD-013（macro 驅動商品）、COPX-010（雙向均失敗）、
      FCX-011（3% vol 個股）、TSLA-014（3.72% vol 個股）
    - 結構性差異：IBIT 雖 3.17% vol 但其 Gap-Down 反轉框架本身即 capitulation
      structure（與 USO/EEM/INDA/VGK 之 BB-lower / 深 pullback 框架同類），
      故 2DD floor 精煉有效；FCX/TSLA/GLD/COPX 框架不具同等 capitulation
      結構，2DD 方向無區分力

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    進場：隔夜 Gap <= -1.5% + Close > Open + 10日回檔 12-25% + WR(10)<=-80
         + 2DD <= -3.0%
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT009Config(ExperimentConfig):
    """IBIT-009 Post-Capitulation Vol-Transition MR 參數"""

    # 進場參數（沿用 IBIT-006 Att2）
    gap_threshold: float = -0.015  # 隔夜開盤跳空 <= -1.5%
    pullback_lookback: int = 10
    pullback_threshold: float = -0.12  # 10日回檔 <= -12%
    pullback_upper: float = -0.25  # 回檔上限 25%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    cooldown_days: int = 10

    # 新增：Post-Capitulation 過濾器（2DD floor 加深方向）
    # Att1=-3.0%（甜蜜點）/ Att2=-2.5%（淺邊界）/ Att3=-4.0%（深邊界）三次迭代結果完全相同，
    # 證實有效門檻範圍 [-2.5%, -4.0%] 廣泛，IBIT-006 失敗訊號集中於 2DD > -2.5% 淺帶。
    twoday_floor: float = -0.03  # 2日累計報酬 <= -3.0%（Att1 甜蜜點）


def create_default_config() -> IBIT009Config:
    return IBIT009Config(
        name="ibit_009_post_cap_vol_transition_mr",
        experiment_id="IBIT-009",
        display_name="IBIT Post-Capitulation Vol-Transition MR",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.045,  # +4.5% (沿用 IBIT-006 Att2)
        stop_loss=-0.04,  # -4.0% (沿用 IBIT-006 Att2)
        holding_days=15,
    )
