"""
XBI-020: ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR

策略方向（Strategy Direction）：
    在 XBI-017 Att1（VIX BANDS Filter Pullback MR，min(A,B) 0.64，repo 首次
    lesson #24 family BANDS 變體，當前全域最優）基礎上，疊加 **^VIX
    forward-looking implied-vol DIRECTION (3d / 5d change) CEILING gate**。

    **Repo 首次 ^VIX DIRECTION 維度應用於 XBI**——XBI-017 為 lesson #24
    family **BANDS** 變體（VIX level 區間），XBI-020 試驗 **DIRECTION** 變體
    （VIX 上升速率 CEILING），與 XLU-013（^MOVE 3d change DIRECTION）/
    USO-025（^OVX 3d DIRECTION）同類維度，首次移植至 FDA 事件驅動生技板塊 ETF。

================================================================================
強制 predict→confirm 預分析（先於建構，決定性命中 → 預測 DOCUMENTED-FAILURE）
================================================================================
XBI-017 Att1（當前全域最優）binding constraint = Part B Sharpe 0.64。
Part B 6 筆交易（執行模型實測）：
    2024-03-14  +3.50% TP   VIX 14.40  3dΔ -0.82  5dΔ -0.04  10dΔ +1.00
    2024-04-25  +3.50% TP   VIX 15.37  3dΔ -1.57  5dΔ -2.63  10dΔ +0.46
    2024-11-18  +3.50% TP   VIX 15.58  3dΔ +1.56  5dΔ +0.61  10dΔ -6.40
    2024-12-19  +3.50% TP   VIX 24.09  3dΔ +9.40  5dΔ +10.17 10dΔ +10.55  ← 最極端上升 VIX winner
    2025-03-31  -5.10% SL   VIX 22.28  3dΔ +3.95  5dΔ +4.80  10dΔ +1.77   ← 唯一殘餘 binding loser
    2025-05-07  +3.50% TP   VIX 23.55  3dΔ +0.87  5dΔ -1.15  10dΔ -4.90

    Part A（2019-2023，11 筆）= 10 × (+3.50% TP) + 1 × (2021-07-19 -0.04%
    near-flat expiry)；Part B = 5 × (+3.50% TP) + 1 × (2025-03-31 -5.10% SL)。
    **兩 Part 所有 winners 皆為相同 +3.50% TP** → 唯一變異源 = Part A 單筆
    near-flat expiry + Part B 單筆 SL（TLT-014 Att3 / XLU-013 zero-variance
    trap 同構）。

    殘餘 binding Part B SL **2025-03-31** = 2025-04-02「Liberation Day」對等
    關稅外生宏觀衝擊（訊號 3/31 觸發、4/1 進場、4/2 盤後關稅宣布、4/3-4 崩盤、
    4/4 -5.10% 停損）。

    **逐維度 separability 分析（SL vs 5 winners，需 SL 為 separable outlier
    且 ≥15pp robust plateau）**：
      - VIX level：SL 22.28 ∈ [14.40, 24.09]，2 winners 更高（24.09 / 23.55）
        → 非可分（亦解釋 XBI-017 BANDS (17,22) 為何未捕捉：22.28 > 22 視同
        broad-panic 而通過）
      - VIX 3d change：SL +3.95 ∈ [-1.57, +9.40]，winner 2024-12-19 **+9.40
        遠高於 SL** → 非可分（CEILING 移除 SL 必先移除 2024-12-19 winner）
      - VIX 5d change：SL +4.80 ∈ [-2.63, +10.17]，winner 2024-12-19 **+10.17
        遠高於 SL** → 非可分
      - VIX 10d change：SL +1.77 ∈ [-6.40, +10.55]，winner 2024-12-19 +10.55
        遠高於 SL → 非可分
      - SPY 20d：SL -3.89%，winner 2024-04-25 -3.76%（僅差 0.13pp）→ knife-edge
        無 ≥15pp robust plateau，非穩健可分
      - XBI 20d：SL -5.25% ∈ [-13.37, +10.82]，2 winners 更負 → 非可分

    **結構性根因**：Part B winner **2024-12-19**（2024-12 鷹派 Fed dot-plot
    拋售，VIX 24 / 3dΔ +9.40 / 5dΔ +10.17）為「高 VIX broad panic →
    systematic V-bounce → XBI MR 獲利」之教科書 XBI U 型 regime（XBI-017
    核心發現）；其 VIX 上升 signature **遠較 SL 2025-03-31 極端**。任何
    ^VIX DIRECTION CEILING 要移除 SL 必先誤殺 2024-12-19 winner（及 Part A
    2022 熊市 V-bounce TPs，皆於 VIX 上升期觸發）。FLOOR 方向不適用（SL 非
    低-VIX-direction outlier）。**與 XBI-016（lesson #25 macro-confirm gate
    FAIL）同根因**：XBI 生技 SLs 多發於 broad-correction 開端、winners 多
    發於 broad-panic V-bounce → 結構鏡像反向（vs IWM）。

    **預測 DOCUMENTED-FAILURE**（predict→confirm 軌跡 3 SUCCESS + 14
    documented，本次為第 15 個 documented）：
      - Att1 (3d CEILING ≤ +5.0，XLU-013 sweet spot 類比)：SL 3dΔ +3.95
        ≤ +5.0 **通過 ceiling 不被移除** → Part B Sharpe TIE 0.64；同時誤殺
        winner 2024-12-19 (+9.40) + Part A 高-VIX-rising TPs → min(A,B) TIE
        或退化 FAIL（SL 非綁定，TSLA-018 Att2 / FXI-015 Att1 同構）
      - Att2 (3d CEILING ≤ +3.0，強制移除 SL +3.95 > +3.0)：SL 移除但
        winner 2024-12-19 (+9.40) 同殺 + Part A 熊市 V-bounce TPs 同殺 →
        非外科式 → Part B 4 純 +3.50% TPs zero-var + Part A 退化 → 雙
        zero-var → min ≈ 0.00 catastrophic REJECT（XBI-017 Att3 /
        XLU-012 Att1/Att2 / EWZ-010 Att2 同構）
      - Att3 (5d CEILING ≤ +5.0，lookback ablation)：SL 5dΔ +4.80 vs winner
        2024-12-19 5dΔ +10.17 同樣交錯、winner 更極端 → 確認無可分
        ^VIX DIRECTION lookback FAIL

================================================================================
策略類型：均值回歸 + 多週期波動 regime gate + ^VIX BANDS + ^VIX DIRECTION
    （Mean Reversion + Vol Regime + Implied Vol Bands + Implied Vol Direction）
================================================================================
基礎（同 XBI-017 Att1，當前全域最優 ★ 2026-05-04）：
- 10 日高點回檔 ∈ [-8%, -20%]
- Williams %R(10) ≤ -80
- ClosePos ≥ 35%
- ATR(20) ≤ 1.10 × ATR(60) vol stability gate
- ^VIX BANDS：VIX <= 17.0 OR > 22.0
- 冷卻 10 日；TP +3.5% / SL -5.0% / 15 天，0.1% 滑價

XBI-020 新增（lesson #24 family DIRECTION 變體；repo 首次於 XBI）：
- **^VIX DIRECTION CEILING**：VIX (lookback 日) change <= max_vix_change
- 訊號通過條件：(VIX_Close − VIX_Close.shift(lookback)) <= max_vix_change

基準對照（XBI-017 Att1 ★ 2026-05-04 全域最優）：
- Part A 11/90.9%/Sharpe 3.12；Part B 6/83.3%/Sharpe 0.64；min(A,B) 0.64
驗收目標：min(A,B) > 0.64 且維持 A/B 平衡（年化 cum diff < 30%、訊號比
gap < 50%）。**預分析預測無法達標（documented-failure）**。
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI020Config(ExperimentConfig):
    """XBI-020 ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR 參數"""

    # === 進場指標（同 XBI-017 Att1 / XBI-015 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # === 多週期波動 regime gate（同 XBI-017 Att1 / XBI-015 Att2）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.10
    use_vol_regime: bool = True

    # === ^VIX BANDS regime gate（同 XBI-017 Att1）===
    vix_ticker: str = "^VIX"
    vix_low_threshold: float = 17.0
    vix_high_threshold: float = 22.0
    use_vix_bands: bool = True

    # === ^VIX DIRECTION CEILING gate（XBI-020 核心新增）===
    # 訊號通過條件：(VIX_Close − VIX_Close.shift(lookback)) <= max_vix_change
    # 迭代紀錄（predict→confirm，**3 次迭代全 CONFIRMED 預測 = DOCUMENTED-FAILURE**）：
    #   Att1 ★（lookback=3, max_vix_change=+5.0，XLU-013 sweet spot 類比）
    #     Part A 9/100%/Sharpe **0.00** zero-var cum +36.29%
    #     Part B 5/80.0%/Sharpe **0.52** cum +8.90%
    #     min(A,B) **0.52**（-19% vs XBI-017 Att1 0.64）FAIL —
    #     SL 2025-03-31 (3dΔ +3.95 ≤ +5.0) **通過 ceiling 不被移除（非綁定）**，
    #     反誤殺 winner 2024-12-19 (3dΔ +9.40) + Part A 變異源 2021-07-19
    #     expiry → Part A zero-var、Part B 仍含 SL（TSLA-018 Att2 / FXI-015
    #     Att1 同構：SL 非綁定，gate 非外科式殺 winner）
    #   Att2（lookback=3, max_vix_change=+3.0，強制移除 SL，+3.95 > +3.0）
    #     Part A 7/100%/Sharpe **0.00** zero-var cum +27.23%
    #     Part B 4/100%/Sharpe **0.00** zero-var cum +14.75%
    #     min(A,B) **≈0.00** catastrophic REJECT — SL 移除但 winner
    #     2024-12-19 (+9.40) + Part A 熊市 V-bounce TPs 同殺 → **雙
    #     zero-var**（† 慣例不適用雙退化）（XBI-017 Att3 / XLU-012
    #     Att1/Att2 / EWZ-010 Att2 同構）
    #   Att3（lookback=5, max_vix_change=+5.0，lookback ablation）
    #     Part A 8/100%/Sharpe **0.00** zero-var cum +31.68%
    #     Part B 5/80.0%/Sharpe **0.52** cum +8.90%
    #     min(A,B) **0.52** FAIL — SL 2025-03-31 (5dΔ +4.80 ≤ +5.0) 同樣
    #     **通過 ceiling 不被移除**，winner 2024-12-19 (5dΔ +10.17) 同殺 →
    #     確認無可分 ^VIX DIRECTION lookback（3d/5d 皆 SL 非綁定）
    # **結論：XBI-017 Att1 (min(A,B) 0.64) 仍為 XBI 全域最優。documented-failure
    #   延伸 lesson #24 family DIRECTION 變體邊界 + 「idiosyncratic
    #   non-separable single residual SL」family（XBI = FDA 事件驅動生技板塊
    #   ETF，殘餘 SL 為外生關稅宏觀衝擊，與 broad-panic V-bounce winner
    #   2024-12-19 結構交錯且 winner VIX-rising 更極端）。predict→confirm 軌跡
    #   3 SUCCESS + 15 documented 全部命中。**
    # 預設 = Att1（least-bad，XLU-013 sweet-spot 類比，repo 慣例保留最佳嘗試）
    vix_direction_lookback: int = 3
    max_vix_change: float = 5.0
    use_vix_direction: bool = True

    cooldown_days: int = 10


def create_default_config() -> XBI020Config:
    """建立預設配置（Att1：vix_direction lookback=3, max_vix_change=+5.0）"""
    return XBI020Config(
        name="xbi_020_vix_direction_mr",
        experiment_id="XBI-020",
        display_name="XBI ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
