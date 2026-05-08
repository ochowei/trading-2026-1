"""
TSM-013: TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback

策略方向（Strategy Direction）：
    Cross-asset Pair Divergence as Regime Filter（cross-asset divergence regime gate）。
    在 TSM-011 Att3（RS Momentum Pullback + 5d return CEILING +10.5%，min(A,B) 0.83，
    全域最優）基礎上，疊加 **TSM - QQQ 20 日報酬差 CEILING 過濾**
    （lesson #19 family v3 / lesson #26 family v2 cross-asset divergence regime gate
    應用，repo 第 6 次 cross-asset divergence regime gate 跨資產移植，repo 首次於
    半導體 ADR 個股 + RS Momentum Pullback 框架）。

跨資產移植動機（Cross-Asset Port Motivation）：
    既有 cross-asset divergence regime gate 成功案例：
        - TLT-014 (TLT-SPY 20d FLOOR, 利率 vs 股票 MR)
        - TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤 BB Squeeze)
        - INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM MR)
        - EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM MR)
        - NVDA-021 (NVDA-QQQ 20d CEILING, 高波動 AI 個股 vs 大盤 MBPC)
    TSM-013 為 repo 首次將 cross-asset divergence regime gate 移植至：
        (a) 半導體 ADR 個股類別（multi-driver: 中國地緣政治 + 半導體景氣 + 客戶集中度）
        (b) **RS Momentum Pullback 框架**（先前皆於 MR / BB Squeeze / MBPC）

    **核心假說（TSM-QQQ Rally Exhaustion CEILING Hypothesis）**：
        TSM RS Momentum Pullback 訊號日，TSM 過去 20 日報酬若顯著超越 QQQ
        （>= +X%），代表 TSM 已脫離 broad-tech regime 進入「single-stock rally
        exhaustion」狀態，即使 TSM-SMH RS >= +5% + 5d 淺回檔 + 5d return <= +10.5%
        三重過濾通過，後續趨勢延續概率仍因 single-stock momentum mean-reversion
        而下降。相對地，當 TSM - QQQ 20d divergence ≤ +X%，TSM 動能伴隨 broad
        tech leadership，RS momentum 高品質訊號不被 ceiling 過濾。

    與 TSM-008 既有 RS（TSM-SMH ≥ +5%）的關係：
        - TSM-008：TSM-SMH 20d ≥ +5% 為「進場觸發條件」（要求 TSM 必須積極跑贏
          半導體板塊，min 0.79）
        - TSM-013：TSM-QQQ 20d ≤ +X% 為「regime 過濾器」（**反向**：排除 TSM
          已過度跑贏 broad market 的 rally exhaustion regime）
        - **兩者方向相反**：TSM-008 要求高 sector RS，TSM-013 過濾極高 broad-market RS
        - QQQ（TSM 非權重股）較 SMH（TSM ~5-7% 權重）為更獨立 anchor，
          提供更乾淨的 TSM-specific rally exhaustion 訊號

    與 TSM-004 SMH 確認（已驗證失敗）的區分：
        - TSM-004：要求 SMH 自身有回檔（lesson #25 family）— FAILED
        - TSM-013：TSM - QQQ relative strength CEILING，非 broad-market absolute
          return 而是 cross-asset relative performance
        - 兩者結構正交：TSM-004 為 absolute regime confirmation，TSM-013 為 relative
          regime divergence（NVDA-016 vs NVDA-021 平行）

    與 lesson #5「趨勢濾波器+均值回歸=災難」的明確區分（同 NVDA-021 / TSLA-017
    / TLT-014 論證）：
        - lesson #5：原本針對「same-asset trend filter + MR」
        - 本實驗：(a) 進場為 momentum continuation 而非 MR、(b) divergence 為
          「跨資產 multi-week relative performance regime classifier」而非 TSM
          自身方向過濾，未違反 lesson #5

策略類型：相對強度動量回調 + 訊號日 5d 報酬 CEILING + 跨資產相對表現 regime gate
    （RS Momentum Pullback + Signal-Day 5d CEILING + Cross-Asset Divergence Filter）

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
TSM-013 新增（lesson #26 family v2 cross-asset divergence CEILING）
================================================================================
- **TSM 20 日報酬 - QQQ 20 日報酬 ≤ max_relative_return**
- Att1（baseline）: max_relative_return = +0.15（+15%，寬鬆 ceiling）
- Att2: max_relative_return = +0.10（+10%，中度）
- Att3: 視結果調整

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
class TSM013Config(ExperimentConfig):
    """TSM-013 TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback 參數"""

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

    # === TSM-QQQ Cross-Asset Divergence CEILING（TSM-013 核心新增）===
    # 訊號通過條件：TSM 20d 報酬 - QQQ 20d 報酬 <= max_relative_return
    # （CEILING 方向：過濾 TSM 已過度跑贏 QQQ 的 rally exhaustion regime）
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    max_relative_return: float = 0.10
    use_divergence_filter: bool = True


def create_default_config() -> TSM013Config:
    return TSM013Config(
        name="tsm_013_qqq_divergence_rs",
        experiment_id="TSM-013",
        display_name="TSM TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
