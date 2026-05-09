"""
TSM-020: TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback

策略方向（Strategy Direction）：
    Cross-asset Pair Divergence as Regime Filter（cross-asset divergence regime gate）。
    在 TSM-011 Att3（RS Momentum Pullback + 5d return CEILING +10.5%，min(A,B) 0.83，
    全域最優）基礎上，疊加 **TSM - SOXX 20 日報酬差 CEILING 過濾**
    （lesson #19 family v3 / lesson #26 family v2 cross-asset divergence regime gate
    應用，**repo 首次「sector-internal anchor」變體於任何資產**——SOXX 為 iShares
    Semiconductor ETF，TSM 約 9% 權重，較 broad-market QQQ（TSM 非權重股）為更
    sector-specific anchor）。直接回應 TSM-019 AI_CONTEXT 列出之未驗證方向 (a)
    SOXX 半導體指數 anchor。

跨資產移植動機（Cross-Asset Port Motivation）：
    既有 cross-asset divergence regime gate 成功案例：
        - TLT-014 (TLT-SPY 20d FLOOR, 利率 vs 股票 MR)
        - TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤 BB Squeeze)
        - INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM MR)
        - EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM MR)
        - NVDA-021 (NVDA-QQQ 20d CEILING, 高波動 AI 個股 vs 大盤 MBPC)
        - EWT-010 (EWT-EEM 20d AND 60d CEILING, 半導體 EM 國家 vs 大盤 EM 雙時框 MR)

    既有 TSM 跨資產 divergence 嘗試（皆 binding 為 Part B 0.83 sample size）：
        - TSM-013 (TSM-QQQ 20d CEILING) — Att1 Part A zero-var all TPs SUCCESS,
          Part B 結構性無區分力, min 0.83 TIE baseline
        - TSM-014 (TSM-QQQ 20d BAND) — Part B SLs (2024-07-08, 2024-10-30) 落在
          winners 分布中段 [+1.48%, +12.37%]，threshold sweep REJECT
        - TSM-015 (TSM-AAPL 20d FLOOR) — repo 首次主要客戶 anchor, Part B SLs
          AAPL-divergence 維度仍重疊
        - TSM-019 (^VIX3M / ^VIX term structure FLOOR) — Att2 Part A 突破 +29%
          但 A/B cum 差 56.5% 違反 30% target

    TSM-020 為 repo 首次 **sector-internal anchor** 變體（SOXX 為 TSM ~9% 權重的
    sector ETF，較 broad QQQ / 主要客戶 AAPL / VIX term structure 不同維度）：
        (a) SMH (TSM-008 entry RS reference, ~12% TSM 權重) 已用作 entry trigger
            而非 regime gate
        (b) SOXX (~9% TSM 權重) 結構為「TSM 在更廣 semi-sector 內的相對位置」
            anchor — 與 SMH 互補但更分散（SOXX top 10 holdings 約佔 60% vs SMH
            約 75%）

    **核心假說（TSM-SOXX Sector-Internal Rally Exhaustion CEILING Hypothesis）**：
        TSM RS Momentum Pullback 訊號日，TSM 過去 20 日報酬若顯著超越 SOXX
        sector ETF（>= +X%），代表 TSM 已脫離 broad semi-sector regime 進入
        「stock-specific rally exhaustion」狀態（即使 TSM-SMH RS >= +5% +
        5d 淺回檔 + 5d return <= +10.5% 三重過濾通過，後續趨勢延續概率仍因
        sector-internal momentum mean-reversion 而下降）。

        **vs TSM-013 (QQQ anchor) 的維度差異**：
        - QQQ anchor: TSM vs broad tech regime（macro tech 環境 + tech leadership）
        - SOXX anchor: TSM vs semi-sector internal positioning（intra-sector
          rotation + competitor 動能）
        - 理論上 SOXX 對 Part B 2024-07-08 / 2024-10-30 SLs 之分離力可能高於
          QQQ：當期 TSM 急跌可能伴隨 NVDA/AVGO/AMD（同 SOXX 大權重）相對
          穩定（地緣政治單獨衝擊 TSM Taiwan exposure），則 TSM-SOXX divergence
          負值；vs TSM-QQQ divergence 因 broad tech 同步壓力而 inconclusive

    與 lesson #25「broad-market 為主要驅動因子的 sub-segment ETF」的明確區分：
        - lesson #25 適用於「target 為 sub-segment + anchor 為其上層 broad
          benchmark」（IWM small-cap → QQQ broad, ✓）
        - 本實驗：TSM 為 SOXX 約 9% 權重之 sub-component，方向為「component vs
          sector ETF」divergence（非 sub-segment vs broad-market），對應
          lesson #20 v3 family v10 結構（EEM-FXI broad-vs-sub-component 失敗
          鏡像反向：sub-component-vs-sector）
        - 自我參考效應：TSM 9% 權重在 SOXX 中相對溫和（vs EEM-FXI 失敗案例
          FXI 為 EEM 30% 權重），自我參考稀釋程度可接受但需驗證

    與 lesson #5「趨勢濾波器+均值回歸=災難」的明確區分（同 NVDA-021 / TSLA-017
    / TLT-014 / TSM-013 論證）：
        - lesson #5：原本針對「same-asset trend filter + MR」
        - 本實驗：(a) 進場為 momentum continuation 而非 MR、(b) divergence 為
          「跨資產 multi-week relative performance regime classifier」而非 TSM
          自身方向過濾，未違反 lesson #5

策略類型：相對強度動量回調 + 訊號日 5d 報酬 CEILING + 跨資產 sector-internal
    relative performance regime gate
    （RS Momentum Pullback + Signal-Day 5d CEILING + SOXX-Sector Divergence Filter）

================================================================================
基礎（同 TSM-011 Att3）
================================================================================
- TSM 20 日報酬 - SMH 20 日報酬 ≥ +5%（相對板塊超額表現）
- 5 日高點回檔 3-7%（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 訊號日 5 日報酬 ≤ +10.5%（rally exhaustion 過濾）
- 冷卻 10 日
- TP +8% / SL -7% / 25 天，0.10% 滑價

================================================================================
TSM-020 新增（lesson #26 family v2 sector-internal divergence CEILING）
================================================================================
- **TSM 20 日報酬 - SOXX 20 日報酬 ≤ max_relative_return_soxx**
- Att1（baseline）: max_relative_return_soxx = +0.10（+10%，loose ceiling，符合
  TSM-013 Att1 +0.15 等價尺度於更窄 sector anchor，因 TSM-SOXX 維度應較
  TSM-QQQ 更窄）
- Att2: 視 Att1 結果調整（surgical sweet spot 可能在 +5% 至 +8% 之間）
- Att3: 視 Att1/Att2 結果決定（若 CEILING 方向 Part B 仍 binding，則改試
  FLOOR 方向 — TSM 落後 SOXX 即 stock-specific 弱勢）

================================================================================
基準對照（TSM-011 Att3 全域最優，2026-05-02）
================================================================================
- Part A: 12 訊號 (2.4/yr), WR 83.3%, 累計 +74.10%, Sharpe 0.86
- Part B: 10 訊號 (5.0/yr), WR 80.0%, 累計 +59.78%, Sharpe 0.83
- min(A,B) 0.83
- A/B 年化 cum diff: 19.3%（< 30% ✓），訊號比 1.2:1（gap 16.7% < 50% ✓）

驗收目標：min(A,B) > 0.83，維持 A/B 平衡（cum diff < 30%, signal gap < 50%）。

================================================================================
迭代歷程（Iteration Log）— 詳見 EXPERIMENTS_TSM.md
================================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSM020Config(ExperimentConfig):
    """TSM-020 TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback 參數"""

    # === RS Momentum Pullback 基礎（同 TSM-011 Att3 / TSM-008）===
    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # === Signal-day return CEILING（同 TSM-011 Att3）===
    ret_1d_max: float = 999.0
    ret_5d_max: float = 0.105

    # === TSM-SOXX Cross-Asset Divergence CEILING（TSM-020 核心新增）===
    # 訊號通過條件：TSM 20d 報酬 - SOXX 20d 報酬 <= max_relative_return_soxx
    # （CEILING 方向：過濾 TSM 已過度跑贏 SOXX 的 sector-internal rally exhaustion）
    benchmark_ticker: str = "SOXX"
    divergence_lookback: int = 20
    # Att1 PARTIAL (max_relative_return_soxx = +0.10, loose ceiling +10%)
    #   → Part A 8/87.5%/Sharpe 1.23 cum +59.23% MDD -7.79%（vs baseline
    #     12/83.3%/0.86/+74.10%, Sharpe +43% / WR +4.2pp / cum -20%）
    #   → Part B 10/80%/0.83 cum +59.78% **完全 unchanged**（filter 對 Part B 非綁定）
    #   → min(A,B) **0.83 TIE baseline**（Part B binding，2024-07-16 / 2024-11-04
    #     兩 SL TSM-SOXX 20d_div < +10% 仍通過 ceiling）
    # Att2 REJECT (max_relative_return_soxx = +0.05, tight ceiling)
    #   → Part A **0 signals 結構性過濾**（TSM-SMH RS ≥ +5% 進場條件下，TSM-SOXX
    #     20d_div 結構性 > +5% — SMH TSM ~12% 權重 vs SOXX ~9%，SMH 對 TSM 漲幅
    #     吸收較多使 TSM-SMH < TSM-SOXX，sector entry RS≥+5% 框架下 +5% SOXX
    #     ceiling 為結構性下界）
    #   → Part B 2 signals 1W/1L Sharpe 0.06（嚴重退化，cooldown chain shift
    #     引入新 trade pattern）
    #   → min(A,B) **0.06 REJECT**（-93% vs baseline 0.83）
    # Att3 REJECT (max_relative_return_soxx = +0.07, medium ceiling sweet spot 探尋)
    #   → Part A 4/75.0%/Sharpe 1.06 cum +21.83%（**Part A 訊號 12→4 過嚴流失**
    #     8 個訊號，cum -71%）
    #   → Part B 5/80%/Sharpe **0.83** cum +26.40%（**Part B 訊號 10→5 -50%**，
    #     A/B 年化 cum gap 67% > 30% ❌、A/B 年化訊號比 0.8:2.5 = 68% gap > 50% ❌）
    #   → min(A,B) **0.83 TIE baseline** 但雙 acceptance criteria 違反 → REJECT
    # **預設 Att1**（三次迭代全部 REJECT，Att1 為三者中 Part A 最佳，min(A,B) 0.83
    # TIE baseline 不超越 — TSM Part B 0.83 binding constraint 第 8 次結構性無解確認）
    max_relative_return_soxx: float = 0.10
    use_divergence_filter: bool = True


def create_default_config() -> TSM020Config:
    return TSM020Config(
        name="tsm_020_soxx_divergence_rs",
        experiment_id="TSM-020",
        display_name="TSM TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
