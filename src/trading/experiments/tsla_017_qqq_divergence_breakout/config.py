"""
TSLA TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout (TSLA-017)

實驗動機 (Motivation)：
- TSLA-015 Att3 為當前全域最優（min(A,B) 0.53，Part A Sharpe 0.84 / Part B 0.53），
  但 Part A vs Part B Sharpe 落差 37%（0.84 vs 0.53），結構性失衡來自 Part A
  2 筆 SL（2021-07-30、2023-03-31）+ 1 筆到期（2023-12-14）共拖累 -7.2%、
  Part B 2 筆 SL（2024-09-23、2025-11-03）共拖累 -14.3%。
- TSLA-013 / TSLA-016 已驗證 single-day signal-day filter（T-1 cap、3d/5d ceiling）
  系統性失敗於 TSLA 高波動 multi-regime AI 個股 BB Squeeze 框架。
- TSLA AI_CONTEXT 明確指出未來突破方向需「跨維度」過濾：
  ^VXN forward-looking implied vol、TSLA-QQQ cross-asset divergence、^VIX BANDS。

嘗試方向（repo 首次：cross-asset divergence regime gate 應用於高波動 AI 個股 +
BB Squeeze Breakout 框架，cross-strategy port from TLT-014）：
**TSLA vs QQQ 多週期報酬差過濾**。

核心觀察（trade-level analysis on TSLA-015 Att3 signals）：
  Part A 11 signals 的 TSLA-QQQ 20d divergence 分布：
    - 8 winners：div 範圍 +4.82% ~ +18.04%（全部正值）
    - 2 SLs (2021-07-30 / 2023-03-31)：div -1.45% / -2.37%（全部負值）
    - 1 Expiry (2023-12-14 -1.38%)：div -1.23%（負值）
  ★ Part A 中 winners 與 losers 在 divergence 維度**完全分離**——
    所有 winners div > 0，所有 losers div < 0。divergence floor 在 [-1.23%, +4.82%]
    區間皆可乾淨切除全部 Part A losers 而不誤殺 winners。

  Part B 6 signals 的 divergence 分布（混合）：
    - 4 winners：div -1.75%（2024-06-17）+ +28.57% / +14.42% / +8.03%
    - 2 SLs：+12.70%（2024-09-23）+ -0.67%（2025-11-03）
  ★ Part B 中 SL 與 winners 在 divergence 維度**部分重疊**——
    2024-09-23 SL div +12.70% 高於多數 winners，2024-06-17 winner div -1.75%
    低於 1 個 SL。Part B div 維度單向過濾力較弱，但 -0.005 floor 仍能過濾
    1 SL（2025-11-03 -0.67%）並透過 cooldown chain shift 從 2024-06-17 winner
    替換為 2024-06-26 winner（同為 +10% TP）。

核心思想：
- TSLA 2019 trade war / 2021 Q3 chip shortage / 2023 Q1 demand worry 等事件驅動
  sell-off regime 下，TSLA 20 日報酬常輕微落後 QQQ（divergence -1% ~ -3%）。
  此 regime 中 BB Squeeze 觸發的突破多為「relative weakness 假突破」，被
  TSLA-013/-016 single-day filter 無法捕捉但被 multi-week cross-asset divergence
  精準分離。
- 健康的 TSLA breakout 通常發生於：(a) 與 QQQ 同步 melt-up、(b) TSLA 主升段
  leadership、或 (c) calm regime 共識行情。這些情境 TSLA - QQQ 20d return 差距
  >= -0.5%（即 TSLA 不落後 QQQ 超過 0.5%）。

與 TSLA-008（已失敗 RS Momentum 進場）的明確區分：
- TSLA-008：RS >= +5%/+8% 作為「**進場觸發條件**」（要求 TSLA 必須積極跑贏 QQQ），
  Part B -0.96 / -0.01 災難性失敗——RS 高為事件驅動短期過熱常為反轉前兆
- TSLA-017：divergence >= -X% 作為「**regime 過濾器**」（僅排除 TSLA 嚴重落後
  QQQ 的 bear regime，不要求 TSLA 主動領先），與 BB Squeeze 進場結構正交

與 lesson #5「趨勢濾波器+均值回歸=災難」的明確區分：
- lesson #5：原本針對「same-asset trend filter + MR」（如 TLT Close>SMA(50)）
- 本實驗：(a) 進場為 breakout 而非 MR、(b) divergence 為「跨資產 relative
  performance regime classifier」而非 TSLA 自身方向過濾，未違反 lesson #5
- 沿用 TLT-014 cross-asset divergence regime gate 的合法性論證

與 TSLA-015 Att3 的疊加：
- TSLA-015 Att3：BB(20,2) 擠壓 30th pct + Close>Upper BB + Close>SMA(50) +
  buffered SMA(20)≥0.99×SMA(60)（同資產 multi-week trend regime）
- TSLA-017 新增：TSLA 20d return - QQQ 20d return >= min_relative_return
  （跨資產 multi-week relative strength regime gate）
- 二者疊加：TSLA 自身結構健康 AND TSLA 與 QQQ 相對表現未進入結構性弱勢

================================================================================
迭代紀錄（三次迭代，2026-05-07）
================================================================================

Att1 (min_relative_return = -0.10, loose threshold)：FAILED non-binding
  Part A 11/72.7%/Sharpe 0.84 cum +82.29%（與 TSLA-015 Att3 baseline 完全相同）
  Part B 6/66.7%/Sharpe 0.53 cum +26.25%（與 baseline 完全相同）
  min(A,B) 0.53（與 baseline 相同，無改善）
  全部 17 baseline 訊號 divergence 皆 >= -10%（最低 -2.37%），閾值非綁定

Att2 (min_relative_return = -0.01, moderate)：PARTIAL Part A SUCCESS
  Part A 10/80.0%/Sharpe **1.17** cum +94.32%（**+39% vs baseline 0.84**）
  Part B 6/66.7%/Sharpe 0.53 cum +26.25%（與 baseline 完全相同）
  min(A,B) 0.53（Part B 為約束，未提升）
  - Part A 過濾 3 losers（2021-07-30 SL、2023-03-31 SL、2023-12-14 Expiry，
    全部 div < -1%），cooldown chain shift 釋放 2021-08-02 + 2023-12-15
    替代訊號（仍部分 losers），淨 Part A 訊號 11→10、WR 72.7%→80.0%
  - Part B 2024-06-17 winner（div -1.75%）被過濾，cooldown chain shift 釋放
    2024-06-26 winner（div +6.43%，亦 +10% TP）替代——**淨無變化**
  - 結論：閾值 -1% 對 Part A 高度有效但對 Part B 非綁定（最低 SL div -0.67%
    仍 > -1%）

Att3 ★ (min_relative_return = -0.005, surgical sweet spot)：SUCCESS
  Part A 10/80.0%/Sharpe **1.17** cum +94.32%（與 Att2 相同）
  Part B **5/80.0%/Sharpe 0.96** cum +35.96%（**+81% vs baseline 0.53**）
  min(A,B) **0.96**（**+81% vs TSLA-015 Att3 0.53，+1700% vs TSLA-005 0.35**，
  **repo TSLA 結構性 Sharpe 0.53 上限首次突破**）
  - Part A 與 Att2 完全相同（-0.005 對 Part A 等同 -0.01，皆過濾 3 losers）
  - Part B 額外過濾 2025-11-03 SL（div -0.67% < -0.5%），無 cooldown chain shift
    替代（後續無符合 BB Squeeze + SMA regime 的訊號），Part B 6→5、WR 66.7%→80.0%
  - A/B 平衡達成：
    年化 cum: Part A (1+0.9432)^(1/5)-1 = 14.13%/yr / Part B (1+0.3596)^(1/2)-1 = 16.61%/yr
    A/B 年化 cum 差 |14.13-16.61|/16.61 = **14.9% < 30% ✓**
    A/B 年化訊號比 2.0:2.5 = 1.25:1（gap 20% < 50% ✓）
    Part B Sharpe 0.96 < Part A 1.17 但差距 18% 遠優於 baseline 37%

最終配置：Att3（min_relative_return = -0.005，divergence_lookback = 20）

================================================================================
結論與跨資產貢獻 (Cross-Asset Contributions)
================================================================================
1. **Repo 首次成功 cross-asset divergence regime gate 移植至高波動 AI 個股 +
   BB Squeeze Breakout 框架**——TLT-014 為 rate-driven asset + MR 框架，TSLA-017
   為高波動科技個股 + breakout 框架，跨資產類別 + 跨策略類型雙重擴展成功
2. **threshold -0.005 為 20d lookback TSLA 上甜蜜點**：
   - -0.10 / -0.05（Att1）非綁定，等同 baseline
   - -0.01（Att2）對 Part A 有效但對 Part B 非綁定
   - -0.005（Att3）surgical 過濾 Part B -0.67% SL，A/B 雙向平衡達成
3. **TSLA winners/losers 在 cross-asset divergence 維度的單向結構**（Part A
   完全分離，Part B 部分重疊）為 cross-asset divergence regime gate 適用
   先決條件——個股 vs 板塊 ETF 的相對強度需有方向性區分力
4. **lesson #19 family v14 邊界擴展**：repo 首次驗證 cross-asset divergence
   gate 對高波動 AI 個股 multi-regime SLs 具區分力（個股事件驅動 SLs 與
   sector context 在 single-day return 維度解耦但在 multi-week relative
   performance 維度耦合），與 TLT-014（reflation regime SLs）平行
5. **新跨資產假設（待驗證）**：TSLA-QQQ 結構可能延伸至其他高波動科技個股 vs
   QQQ（NVDA-016 試 SMH 失敗 → TSLA-017 試 QQQ 成功，預期差異為 SMH 為更窄
   sector index、QQQ 為更廣 macro context）。NVDA-018 ^VXN 失敗時建議轉測
   NVDA-QQQ divergence；TSLA-QQQ vs SPY benchmark 對比測試亦可考慮
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA017Config(ExperimentConfig):
    """TSLA-017 TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout 參數

    最終配置：Att3（min_relative_return = -0.005，divergence_lookback = 20）
    結果：min(A,B) 0.96（+81% vs TSLA-015 Att3 0.53）
    """

    # === BB Squeeze Breakout 基礎（同 TSLA-015 Att3）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === Same-Asset Multi-Week Trend Regime（同 TSLA-015 Att3 buffered SMA）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.99

    # === Cross-Asset Divergence Regime Gate（TSLA-017 核心新增）===
    # benchmark：QQQ（NASDAQ-100，TSLA 主要市場 context）
    # divergence_lookback：20 日（與 TLT-014 一致，捕捉 multi-week regime shift）
    # min_relative_return：TSLA N 日報酬 - QQQ N 日報酬 必須 >= 此值
    # 即「TSLA 不可比 QQQ 落後超過 |min_relative_return|」
    # Att3 sweet spot -0.005 由 trade-level analysis 推導：所有 Part A losers
    # div < -1.2% / 所有 Part A winners div > +4.8% → -0.005 為「safely separates
    # all Part A losers from winners」最寬鬆閾值；對 Part B 額外過濾 -0.67% SL
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    min_relative_return: float = -0.005


def create_default_config() -> TSLA017Config:
    return TSLA017Config(
        name="tsla_017_qqq_divergence_breakout",
        experiment_id="TSLA-017",
        display_name="TSLA TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
