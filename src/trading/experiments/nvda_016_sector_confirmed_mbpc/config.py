"""
NVDA-016: Sector-Health Confirmed Multi-Week Regime-Aware MBPC
            (SMH Sector Context Confirmation Gate, mirror of IWM-015 lesson #25 family)

策略方向（Strategy Direction）：
    在 NVDA-013 Att3（Multi-Week Regime-Aware MBPC，min(A,B) 0.55，repo 第 1 次
    lesson #22 cross-strategy 移植至 MBPC + 第 1 次發現 vol regime 在非 BB Squeeze
    框架非冗餘）基礎上，疊加 **SMH 5/10 日報酬作為跨資產半導體板塊健康確認閘門**，
    要求半導體 sector ETF（NVDA 同一 sub-sector 代理）已處於健康／非顯著
    risk-off regime，才放行 NVDA 動量延續訊號。

跨資產移植動機（Cross-Asset Mirror Inversion of IWM-015 Hypothesis）：
    IWM-015 ★（QQQ 10d ≤ -1.5%）為 repo 首次「broad-market 修正確認 gate」用於
    MR/dip-buying 訊號（min(A,B) 0.59→2.80, +374%）。lesson #25 假設 broad
    cap-segment ETF 適用，sector ETF 不適用（XBI-016 失敗、COPX-013 失敗）。

    **NVDA-016 於 MBPC 框架翻轉方向**：
        - IWM-015 (MR / dip-buying)：要求 broad market **同步** capitulation
          （macro 10d ≤ -X%）→ V-bounce regime
        - NVDA-016 (MBPC / 動量延續)：要求 sector **健康** 持續上行
          （macro N d ≥ -X%）→ trend continuation regime
    兩者 mirror 同一假設「個股技術面訊號需 broader-context regime confirmation
    才有效」，但對 MR vs 動量延續的 confirmation 方向相反（MR 需同步衰弱、動量
    需同步健康）。

    **Repo 較少使用方向**：
        既有 cross-asset 過濾多為（a）pair trading RS 對沖（NVDA-006/TSM-007 等），
        （b）external indicator gate（^MOVE/^OVX/^GVZ implied vol direction filter，
        僅 5 次驗證），（c）broad-market context confirmation（IWM-015 ★ 唯一成功，
        XBI-016 / COPX-013 失敗）。本實驗為 repo 第 4 次 broad-market context
        confirmation 嘗試（首次於高波動 AI 個股 + MBPC 動量延續框架）。

================================================================================
基準：NVDA-013 Att3（2026-04-26 全域最優）
================================================================================
- Part A: 26 訊號, WR 73.1%, 累計 +139.54%, Sharpe **0.55**
- Part B:  7 訊號, WR 85.7%, 累計  +58.62%, Sharpe **2.44**
- min(A,B) **0.55**（Part A 為約束）
- A/B 年化 cum diff: 26.4%（< 30% ✓），訊號比 1.49:1（gap 33% < 50% ✓）

驗收目標：min(A,B) > 0.55，維持 A/B 平衡（cum diff < 30%、訊號比 < 50%），
        且使用 less-used direction（cross-asset sector context confirmation）。

================================================================================
NVDA-013 Att3 Trade-Level SMH 維度分析（pre-experiment research）
================================================================================
Part A 7 SLs 的 SMH 5d / SMH 10d / NVDA-SMH 10d divergence 分布：
| Date       | Result | SMH_10d | SMH_5d  | NVDA-SMH_10d |
|------------|--------|---------|---------|--------------|
| 2019-02-20 | SL     | +4.56%  | +1.84%  | +1.17%       |
| 2020-10-20 | SL     | +4.63%  | -1.94%  | -5.29%       |
| 2021-02-18 | SL     | +6.09%  | +2.27%  | +3.50%       |
| 2021-04-21 | SL     | -1.56%  | -0.43%  | +10.16%      |
| 2022-04-04 | SL     | +0.46%  | -2.72%  | +1.88%       |
| 2023-07-25 | SL     | +3.35%  | -2.41%  | +4.37%       |
| 2023-08-28 | SL     | +0.18%  | -0.07%  | +6.86%       |

**SMH 5d >= 0% 過濾命中**：5/7 SLs（2020-10-20、2021-04-21、2022-04-04、
2023-07-25、2023-08-28）；保留 2/7 SLs（2019-02-20、2021-02-18）。

**問題**：SMH 5d 與 SMH 10d 維度上 SLs 與 TPs 分布**廣泛重疊**，無單向區分線：
- TPs 中亦有大量 SMH 5d < 0% 訊號（2019-12-03 -3.43%、2020-01-27 -2.99%、
  2022-12-07 -5.01% 等），SMH 5d >= 0% 過濾誤殺多筆好訊號。

================================================================================
迭代歷程（Iteration Log，已執行三次）
================================================================================
Att1: SMH 10d return >= 0%（嚴格 sector uptrend 閘門）— FAILED min 0.41
    結果：Part A 19 訊號 / WR 68.4% / Sharpe **0.41** cum +62.56%
          Part B 4 訊號 / WR 75.0% / Sharpe 1.72 cum +25.92%
    失敗分析：
        - SMH 10d 為平滑指標，無法精準分辨 SLs：26 baseline 訊號中 7 被過濾，
          僅 1 SL（2021-04-21）被過濾，其餘 6 SLs 全部保留（baseline SLs 多
          發生於 SMH 10d > 0% 的 sector uptrend 期間）
        - 同時誤殺 6 baseline TPs（2019-03-08、2019-12-03、2020-01-27、
          2021-08-12、2022-12-07、2023-03-13、2023-04-21）
        - cooldown chain shift 引入新 SLs 進一步壓低 Part A WR 至 68.4%

Att2: SMH 10d return >= -5%（寬鬆 sector 未深度修正）— FAILED 非綁定
    結果：Part A 26 訊號 / WR 73.1% / Sharpe **0.55** cum +139.54%
          Part B 7 訊號 / WR 85.7% / Sharpe 2.44 cum +58.62%
    分析：與 NVDA-013 baseline **完全相同**——baseline 所有 33 訊號的 SMH 10d
          皆 >= -5%（最深僅 -3.74%，2019-12-03 TP），閾值在此區間完全非綁定。
          證實 SMH 10d 維度無有效 sector-weakness 過濾邊界。

Att3: SMH 5d return >= 0%（短週期嚴格 sector 健康閘門）— PARTIAL
    結果：Part A 9 訊號 / WR **77.8%** / Sharpe **0.62** cum +37.31%
                  (filtered 5/7 baseline SLs + 12/19 baseline TPs/expiries)
          Part B 3 訊號 / WR **100%** / Sharpe 0.00 std=0 zero-var cum +25.97%
                  (全部 3/3 TPs，原 baseline Part B 7 訊號中保留 3，移除 4)
    min(A,B)† **0.62**（Part A binding，Part B std=0 沿用 EWJ-003/SPY-009/
                       DIA-012/IWM-013/IBIT-009 慣例：Part B 結構性零方差時採
                       Part A Sharpe 為 min 約束）, **+12.7% vs NVDA-013 0.55**

    **A/B 平衡檢查（部分達成）**：
        - Part A 年化 cum: (1+0.3731)^(1/5)-1 = 6.55%/yr
        - Part B 年化 cum: (1+0.2597)^(1/2)-1 = 12.23%/yr
        - cum gap: |12.23-6.55|/12.23 = **46.4% > 30% ❌（未達 30% 目標）**
        - 訊號比 1.8/yr vs 1.5/yr = 16.7% gap < 50% ✓
        - WR 77.8% vs 100% = 22.2pp（與 baseline NVDA-013 12.6pp 對比劣化）

    **部分達成評估**：
        ✓ Sharpe 改善：0.55 → 0.62（+12.7%）
        ✓ Part A WR 改善：73.1% → 77.8%（+4.7pp）
        ✓ Less-used direction 探索（repo 第 4 次 broad-market context
          confirmation gate，首次於 MBPC + 高波動 AI 個股）
        ✗ A/B 累計差 46.4%（baseline 26.4%）— SMH 5d >= 0% 過濾後 Part A
          訊號數崩減（26→9），絕對累計報酬下降 73%（139.54% → 37.31%），
          雖 risk-adjusted 指標改善但 absolute return 大幅縮減
        ✓ A/B 訊號比 16.7% < 50% ✓

    **threshold 邊界 sweep（已測試）**：
        SMH 5d >= -5%： 26 訊號 Sharpe 0.55（baseline，非綁定）
        SMH 5d >= -2%： 19 訊號 Sharpe 0.55（=baseline）
        SMH 5d >= -0.5%：15 訊號 Sharpe 0.53（劣化）
        SMH 5d >=  0% ★：9 訊號 Sharpe **0.62**（甜蜜點）
        SMH 5d >= +0.5%：8 訊號 Sharpe 0.52（過嚴）

    **失敗模式分析（lesson #25 family v6 邊界擴展）**：
        - lesson #25 broad-market context confirmation gate **不適用於 MBPC
          動量延續框架 + 高波動 AI 個股**
        - 失敗根因：NVDA Part A SLs 在 SMH 5d/10d 維度分布**雙向發散**
          （5d -2.72% ~ +2.27%、10d -1.56% ~ +6.09%），其中 NVDA 個股事件
          驅動 SLs（earnings drift、ATH reversal、tech selloff）與 sector
          context 解耦——sector 健康時 NVDA 仍可單獨反轉
        - sector 過濾僅能剔除 sector-wide weakness 期 SLs（2-3 筆），無法
          區分多 regime 的 NVDA-specific event 性 SLs
        - 5d 短週期較 10d 區分力較強但仍未達 surgical threshold

================================================================================
跨資產失敗家族擴展（Cross-Asset Failure Family Expansion）
================================================================================
**lesson #25 失敗清單更新**（4 次跨資產測試結果）：
1. ✓ IWM-015 ★ Att1（小型股寬基 ETF + MR 框架，QQQ 10d <= -1.5%）：min 2.80
2. ✗ XBI-016（生技板塊 ETF + MR 框架，QQQ/SPY 10d）：min -0.55/zero-var/0.34
3. ✗ COPX-013（礦業板塊 ETF + MR 框架）：3 次嘗試全失敗
4. ✗ NVDA-016（高波動 AI 個股 + MBPC 框架，SMH N 日 mirror inversion）：
   Att1 0.41 / Att2 0.55 / Att3 0.62 部分（Sharpe ✓ but A/B cum gap ✗）

**精煉跨資產規則（lesson #25 v3）**：
    Cross-asset broad-market / sector context confirmation gate 適用條件：
    (a) **資產類別**：broad cap-segment ETF（IWM small-cap、MDY mid-cap、
        SPLG large-cap）— 結構單一驅動類型，個股 SLs 與 broad market 高度
        相關
    (b) **策略框架**：MR / dip-buying（gate 方向：要求 macro 同步 capitulation）
    (c) **SLs 結構**：SLs 來自「broad-market 健康時的孤立 cap-segment 急殺」
        （Omicron / SVB 等 isolated event）

    **結構性失敗條件**：
    (a) 事件驅動 sector ETF（XBI biotech FDA / COPX 礦業商品價格）— SLs 多發
        於 broad-market 同步修正期，gate 無法區分
    (b) 多 driver 高波動個股（NVDA earnings/ATH/AI hype）— SLs 與 sector
        context 解耦，sector 過濾誤殺多於正確過濾
    (c) MBPC / 動量延續框架（要求 macro 健康）— sector uptrend 期反而是
        NVDA 個股反轉風險最高時段（lesson #5 邊界：均值回歸+趨勢濾波器=災難
        的鏡像版本，動量延續+sector trend 確認亦可能失效）

================================================================================
建議的後續方向
================================================================================
NVDA-016 失敗確認 lesson #25 不適用於高波動 AI 個股 MBPC 框架。NVDA Sharpe
0.55 可能已達 13 次實驗 + 40+ 次嘗試後的結構性上限，未來改進方向需脫離
現有 entry-time / single-day filter 與 cross-asset macro gate 框架，可探索：
- ^VXN（Nasdaq-100 implied vol）BANDS regime gate（XBI-017 BANDS 跨資產）
- NVDA earnings calendar 季節性過濾（避開 4 個 earnings windows ±5d）
- NVDA 自身 RSI(2) capitulation depth confirmation（lesson #19 family 自身
  oscillator depth filter，雖 NVDA-011 已試但搭配 MBPC 框架可能不同）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA016Config(ExperimentConfig):
    """NVDA-016 Sector-Health Confirmed MBPC 參數"""

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

    # === 多週期趨勢 regime 過濾（lesson #22，同 NVDA-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 多週期波動 regime 過濾（同 NVDA-013 Att3）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === NVDA-016 新增：SMH 板塊健康確認閘門（lesson #25 mirror inversion）===
    # 三次迭代結果：
    #   Att1 (10d, >=  0.00): FAILED min 0.41 — 過嚴未過濾 SLs，誤殺多 TPs
    #   Att2 (10d, >= -0.05): FAILED 非綁定 = NVDA-013 baseline 0.55
    #   Att3 (5d, >= 0.00) ★: PARTIAL min 0.62 (+12.7% Sharpe, A/B cum gap fails)
    macro_ticker: str = "SMH"
    macro_lookback: int = 5
    macro_min_return: float = 0.0  # Att3 sweet spot：SMH 5d >= 0% 短週期 sector 健康


def create_default_config() -> NVDA016Config:
    """建立預設配置（Att3：SMH 5d >= 0% 短週期 sector 健康閘門）"""
    return NVDA016Config(
        name="nvda_016_sector_confirmed_mbpc",
        experiment_id="NVDA-016",
        display_name=("NVDA Sector-Health Confirmed Multi-Week Regime-Aware MBPC (SMH 5d Gate)"),
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
