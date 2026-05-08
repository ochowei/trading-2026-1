"""
NVDA-021: NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC

策略方向（Strategy Direction）：
    Cross-asset Pair Divergence as Regime Filter（配對交易型 regime gate）。
    在 NVDA-013 Att3（Multi-Week Regime-Aware MBPC，min(A,B) 0.55，全域最優）
    基礎上，疊加 **NVDA - QQQ 20 日報酬差 CEILING 過濾**（lesson #19 family v3 /
    lesson #26 family v2 cross-asset divergence regime gate 應用）。

    **Repo 首次「NVDA - QQQ 跨資產 divergence regime gate（CEILING 方向）」**：
    既有 cross-asset divergence regime gate 成功案例：
        - TLT-014 (TLT-SPY 20d FLOOR, 利率 vs 股票)
        - TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤)
        - INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM)
        - EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM)
        - COPX-014 (CCI 礦業 vs 商品 ETF)
        - USO-026 (oil-related)
        - NVDA-016（mirror inverse: SMH sector context confirmation gate, FAILED）
    NVDA-021 為 repo 首次將 cross-asset divergence regime gate 移植至：
        (a) 高波動 AI mega-cap 個股 + MBPC（Donchian breakout pullback）框架
        (b) **CEILING 方向**（mirror INDA-012 / EWZ-009 outperformer-mean-reversion 結構）

跨資產移植動機（Cross-Asset Port Motivation）：
    NVDA-013 Att3 Part A 7 SLs（trade-level 分析自 NVDA-016 同源 SL list）：
        | Date       | Result | NVDA-SMH_10d |
        |------------|--------|--------------|
        | 2019-02-20 | SL     | +1.17%       |
        | 2020-10-20 | SL     | -5.29%       |
        | 2021-02-18 | SL     | +3.50%       |
        | 2021-04-21 | SL     | +10.16%      |
        | 2022-04-04 | SL     | +1.88%       |
        | 2023-07-25 | SL     | +4.37%       |
        | 2023-08-28 | SL     | +6.86%       |

    **核心觀察：6/7 SLs 集中於 NVDA 顯著跑贏 SMH (NVDA-SMH_10d > 0)，
    其中 5/7 SLs 為 NVDA-SMH_10d ≥ +1.17%。** 反向，2020-10-20 SL 為唯一
    underperform 案例（pre-election uncertainty，非 rally exhaustion）。
    QQQ 為更獨立的廣義基準（NVDA 在 SMH 中為主要成份股，~20% 權重；
    NVDA 在 QQQ 中僅 ~5-12%），故選擇 QQQ 作為 cross-asset divergence anchor
    可提供更乾淨的 NVDA-specific rally exhaustion 訊號。

    **核心假說（NVDA-QQQ Rally Exhaustion CEILING Hypothesis）**：
        NVDA MBPC 訊號日 NVDA 過去 20 日報酬若顯著超越 QQQ（>= +X%），
        代表 NVDA 已脫離 broad-tech regime 進入「single-stock rally exhaustion」
        狀態，即使 Donchian breakout + 5d 淺回檔 + multi-week regime gate 通過，
        後續趨勢延續概率仍因 single-stock momentum mean-reversion 而下降。
        相對地，當 NVDA - QQQ 20d divergence ≤ +X%，NVDA 動能伴隨 broad tech
        leadership，MBPC 高品質訊號不被 ceiling 過濾。

    與 lesson #5「趨勢濾波器+均值回歸=災難」的明確區分（同 TSLA-017 / TLT-014 論證）：
        - lesson #5：原本針對「same-asset trend filter + MR」（如 TLT Close>SMA(50)
          作為 MR 進場濾波器）
        - 本實驗：(a) 進場為 momentum continuation 而非 MR、(b) divergence 為
          「跨資產 multi-week relative performance regime classifier」而非
          NVDA 自身方向過濾，未違反 lesson #5
        - 沿用 TLT-014 / TSLA-017 / INDA-012 / EWZ-009 cross-asset divergence
          regime gate 的合法性論證

    與 NVDA-006 / NVDA-008（已驗證 RS 為進場觸發）的區分：
        - NVDA-006：NVDA-SMH 20d RS ≥ +5% 作為「進場觸發條件」（要求 NVDA 必須
          積極跑贏 SMH），有效 min 0.47（非 regime gate 而是 entry trigger）
        - NVDA-021：NVDA-QQQ 20d divergence ≤ +X% 作為「regime 過濾器」
          （**反向**：排除 NVDA 已過度跑贏 broad market 的 rally exhaustion regime）
        - 兩者方向相反：NVDA-006 要求高 RS，NVDA-021 過濾極高 RS

    與 NVDA-016（已驗證 SMH context confirmation FAILED）的區分：
        - NVDA-016：要求 SMH 自身強勢（SMH 5d/10d ≥ -X%），broad-market
          context confirmation gate（lesson #25 family）— FAILED min 0.41
        - NVDA-021：NVDA - QQQ relative strength CEILING，非 broad-market
          absolute return 而是 cross-asset relative performance
        - 兩者結構正交：NVDA-016 為 absolute regime confirmation，NVDA-021 為
          relative regime divergence

策略類型：趨勢延續 / 動量延續 + 多週期 regime gate + 跨資產相對表現 regime gate
    （Trend / Momentum Continuation + Multi-Week Regime + Cross-Asset Divergence Filter）

================================================================================
基礎（同 NVDA-013 Att3）
================================================================================
- Donchian 20 日新高，breakout freshness ≤ 10 日
- Close > SMA(50)
- 5 日高點回檔 ∈ [-3%, -8%]
- RSI(14) ∈ [40, 65]
- Close > Open（多頭 K 棒）
- SMA(20) ≥ 1.00 × SMA(60)（lesson #22 strict trend regime）
- ATR(20) ≤ 1.40 × ATR(60)（vol regime，MBPC 框架非冗餘）
- 冷卻 10 日
- TP +8% / SL -7% / 20 天，0.15% 滑價

================================================================================
NVDA-021 新增（lesson #26 family v2 cross-asset divergence CEILING）
================================================================================
- **NVDA 20 日報酬 - QQQ 20 日報酬 ≤ max_relative_return**
- Att1（baseline）: max_relative_return = +0.05（+5%，寬鬆 ceiling，鎖定 SLs > +5%）
- Att2: max_relative_return = +0.03（+3%，中度，可能多過濾邊緣 SLs）
- Att3: 視結果調整（縮緊/放寬閾值，或改 lookback 至 10d）

================================================================================
基準對照（NVDA-013 Att3 全域最優，2026-04-26）
================================================================================
- Part A: 26 訊號, WR 73.1%, 累計 +139.54%, Sharpe 0.55
- Part B:  7 訊號, WR 85.7%, 累計  +58.62%, Sharpe 2.44
- min(A,B) 0.55
- A/B 年化 cum diff: 26.4%（< 30% ✓），訊號比 1.49:1（gap 33% < 50% ✓）

驗收目標：min(A,B) > 0.55，維持 A/B 平衡（cum diff < 30%, signal gap < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1 (max_relative_return = +0.05, +5% loose ceiling)：SUCCESS min(A,B) **0.82**
    結果：
        Part A: 15 訊號, WR 80.0%, 累計 +101.64%, Sharpe **0.82**, MDD -10.13%
        Part B:  5 訊號, WR 80.0%, 累計  +35.99%, Sharpe **1.99**, PF 800
        min(A,B): **0.82**（**+49% vs NVDA-013 Att3 baseline 0.55**）
        Part A 訊號 26→15（-42%, 過濾 11 訊號）
        Part A WR 73.1%→80.0%（+6.9pp 品質提升）
    A/B 平衡（驗收目標全達）：
        Part A 年化 cum: (1+1.0164)^(1/5)-1 = 15.07%/yr
        Part B 年化 cum: (1+0.3599)^(1/2)-1 = 16.61%/yr
        A/B 年化 cum 差 |15.07-16.61|/16.61 = **9.3% < 30% ✓**（極佳，遠優於 baseline 26.4%）
        A/B 年化訊號比 3.0:2.5 = **1.2:1**（gap 16.7% < 50% ✓）
    SL 過濾分析：
        Part A 殘留 3 SLs: 2019-02-20（NVDA-SMH +1.17%）/ 2020-10-20（NVDA-SMH -5.29%）/
        2023-08-28（filter 邊緣 NVDA-QQQ < +5%）。Filter 過濾 5+ 個 NVDA-SMH > +5% SLs：
        2021-02-18（+3.50% SMH 但 QQQ 更高）/ 2021-04-21（+10.16%）/ 2022-04-04（+1.88%）
        / 2023-07-25（+4.37%）。
    Repo 首次 cross-asset divergence regime gate（CEILING）成功移植至高波動 AI mega-cap
    個股 + MBPC 框架。

Att2 ★ (max_relative_return = +0.03, +3% moderate)：SUCCESS min(A,B) **1.43**
    結果：
        Part A: 10 訊號, WR **90.0%**, 累計  +85.63%, Sharpe **1.43**
        Part B:  5 訊號（不變）, WR 80.0%, 累計  +35.99%, Sharpe **1.99**
        min(A,B): **1.43**（**+74% vs Att1 0.82**, **+160% vs NVDA-013 baseline 0.55**）
        Part A 訊號 15→10（額外過濾 5）
        Part A WR 80.0%→**90.0%**（+10pp，repo NVDA Part A WR 歷史新高）
        Part A SLs 3→**1**（僅殘留 2019-02-20，移除 2020-10-20 + 2023-08-28）
    A/B 平衡（驗收目標全達）：
        Part A 年化 cum: (1+0.8563)^(1/5)-1 = 13.21%/yr
        Part B 年化 cum: (1+0.3599)^(1/2)-1 = 16.61%/yr
        A/B 年化 cum 差 |13.21-16.61|/16.61 = **20.5% < 30% ✓**
        A/B 年化訊號比 2.0:2.5 = **0.8:1**（gap 25.0% < 50% ✓）
    SL 過濾分析：
        Att1 殘留 2 SLs（2020-10-20、2023-08-28）皆於 +3% 閾值被過濾，唯一殘留
        SL 為 2019-02-20（NVDA-SMH +1.17% 但 NVDA-QQQ < +3%，filter 邊緣）。
        Cooldown chain shift 在 Part A 引入新訊號 2019-09-23（取代 2019-09-17）
        和 2023-04-14（取代 2023-04-05），均為 winners。

Att3 (依 Att2 結果調整)：待執行
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA021Config(ExperimentConfig):
    """NVDA-021 NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC 參數"""

    # === MBPC 基礎（同 NVDA-013 Att3）===
    donchian_period: int = 20
    breakout_recency_days: int = 10
    pullback_lookback: int = 5
    pullback_min: float = -0.03
    pullback_max: float = -0.08
    sma_trend_period: int = 50
    rsi_period: int = 14
    rsi_min: float = 40.0
    rsi_max: float = 65.0
    bullish_close_required: bool = True
    cooldown_days: int = 10

    # === Multi-week SMA trend regime（同 NVDA-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === ATR vol regime（同 NVDA-013 Att3）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === NVDA-QQQ Cross-Asset Divergence CEILING（NVDA-021 核心新增）===
    # 訊號通過條件：NVDA 20d 報酬 - QQQ 20d 報酬 <= max_relative_return
    # （CEILING 方向：過濾 NVDA 已過度跑贏 QQQ 的 rally exhaustion regime）
    benchmark_ticker: str = "QQQ"
    divergence_lookback: int = 20
    max_relative_return: float = 0.03  # Att2: +3% moderate ceiling
    use_divergence_filter: bool = True


def create_default_config() -> NVDA021Config:
    """預設配置（Att2：max_relative_return=+0.03, lookback=20d）"""
    return NVDA021Config(
        name="nvda_021_qqq_divergence_mbpc",
        experiment_id="NVDA-021",
        display_name="NVDA NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
