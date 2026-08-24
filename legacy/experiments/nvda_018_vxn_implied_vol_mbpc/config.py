"""
NVDA-018: ^VXN Forward-Looking Implied-Volatility DIRECTION Regime-Gated MBPC

策略方向（Strategy Direction）：
    將 lesson #24（forward-looking implied volatility derivative 為 backward-looking
    regime gate 飽和後的下一維度）首次跨資產移植至**多 regime 高波動 mega-cap
    個股 + MBPC 框架**。

動機（Motivation）：
    NVDA-013 Att3（Multi-Week Regime-Aware MBPC）為當前全域最優 min(A,B) 0.55，
    但 Part A/B Sharpe 落差仍極大（0.55 vs 2.44，4.4x）。Trade-level 分析顯示
    Part A 7 筆 SLs 散佈於 2019-2023 多 regime：
        2019-02-20（Q4-2018 panic 餘波）
        2020-10-20（pre-election vol）
        2021-02-18（post-pandemic chop）
        2021-04-21（late-bull）
        2022-04-04（bear 早期）
        2023-07-25（summer rally end）
        2023-08-28（late-summer chop）
    SMA(20)≥SMA(60) trend regime 與 ATR(20)≤1.40×ATR(60) vol regime 雙閘門
    無法精準區分這些 multi-regime SLs，因 backward-looking volatility 在訊號日
    仍處於收縮狀態（NVDA-013 已驗證 SLs signal-day SMA/ATR 通過閘門），
    但市場 forward-looking implied vol（^VXN）在訊號前 3-5 日內可能已上升，
    暗示市場參與者 pricing in 即將到來的波動擴張。

    **核心假設**：^VXN（NASDAQ-100 implied volatility index）3 日變化捕捉了
    backward-looking SMA/ATR regime gate 無法識別的「forward-looking 即將
    波動擴張」訊號，能精準過濾上述 7 筆 Part A SLs 中與 implied vol 上升
    相關的子集，同時保留 Part B 純 AI bull regime 訊號（implied vol 通常穩定
    或下降）。

    **Repo 第 5 次 lesson #24 forward-looking IV regime gate 跨資產驗證**：
    繼 TLT-013 (^MOVE LEVEL, +17%)、XLU-013 (^MOVE 3d DIRECTION, +112%)、
    GLD-015 (^GVZ 10d DIRECTION, +55%)、USO-025 (^OVX 3d DIRECTION, +58%) 後，
    **首次驗證於 mega-cap 個股（NVDA），首次驗證 ^VXN 於任何資產，
    首次跨策略類型擴展（既往 4 案例皆於 MR 框架，NVDA-018 為 MBPC 框架）**。

策略類型：趨勢跟蹤 / 動量延續 + 多週期 regime gate + forward-looking IV gate
    （Trend-following + Multi-Week Regime + Forward-looking Implied Vol Filter）

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
NVDA-018 新增（lesson #24 forward-looking IV）
================================================================================
- **^VXN N 日變化 ≤ max_vxn_change**
- 預設 N=3, max_vxn_change=+5.0（從 XLU-013 / USO-025 sweet spot 直接移植）
- ^VXN = CBOE NASDAQ-100 Volatility Index（NASDAQ-100 implied vol，
  NVDA 為 NASDAQ-100 主要成份股，^VXN 為最直接的 forward-looking IV）

================================================================================
基準對照（NVDA-013 Att3 全域最優）
================================================================================
- Part A: 26 訊號, WR 73.1%, 累計 +139.54%, Sharpe 0.55
- Part B:  7 訊號, WR 85.7%, 累計  +58.62%, Sharpe 2.44
- min(A,B) 0.55
- A/B 年化 cum diff: 26.4%（< 30% ✓），訊號比 1.49:1（< 50% ✓）

驗收目標：min(A,B) > 0.55，維持 A/B 平衡（cum diff < 30%, signal gap < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（DIRECTION 3d <= +5.0，XLU-013 / USO-025 sweet spot 直接移植）：FAILED min 0.52
    參數：use_vxn_direction_filter=True, lookback=3, max_change=+5.0
    結果：
        Part A: 25 訊號（vs 26 baseline），WR 72.0%（vs 73.1%），Sharpe **0.52**
        Part B:  7 訊號（不變），WR 85.7%，Sharpe 2.44
        min(A,B): **0.52**（-5.5% vs NVDA-013 baseline 0.55）
    失敗分析：
        - +5.0 threshold 過濾僅 1 筆 Part A 訊號：2023-03-13（VXN 3d +5.31，
          銀行危機 SVB 倒閉日）— 該筆為 TARGET +8% **winner**，非 SL
        - 0 SLs 被過濾：7 筆 Part A SLs 的 VXN 3d_chg 全部 ≤ +2.31
          （max +2.31 於 2021-04-21）
        - 4/7 SLs 的 VXN 3d_chg 為 NEGATIVE（VXN 在訊號前 3 日下降）
        - **核心發現**：NVDA Part A SLs 並非 forward-looking IV spike 引發，
          而是發生於 VXN 平靜或下降的「假性 calm regime」中
        - 與 USO-025（commodity event-driven，^OVX 3d spike 過濾 OPEC 事件）
          結構不同：NVDA 為 broad-index 成份股，^VXN 反映 NASDAQ-100 整體
          市場預期，NVDA 個股的失敗模式與 NASDAQ-100 macro IV 弱相關

Att2（DIRECTION 10d <= 0.0，longer window + tighter direction）：FAILED min 0.17
    參數：use_vxn_direction_filter=True, lookback=10, max_change=0.0
    結果：
        Part A: 19 訊號（vs 26 baseline），WR **57.9%**（vs 73.1%，**-15.2pp**），
                Sharpe **0.17** cum +20.18%（vs +139.54%）
        Part B:  3 訊號（vs 7 baseline），WR 100%，但 std=0 zero-var Sharpe 0.00
        min(A,B): **0.17**（-69% vs NVDA-013 baseline 0.55）
    失敗分析：
        - 嚴重過濾 Part A：26→19，但**移除的 7 筆中僅 1 筆為 SL**，6 筆為 TP
          （2019-09-13 EXP, 2019-10-23 TP, 2020-04-22 TP, 2020-05-28 TP,
           2021-08-12 TP, 2022-08-08 TP, 2023-04-21 TP, 2023-06-27 TP, 2023-11-27 EXP）
        - WR 顯著惡化：73.1% → 57.9%（lesson #19 cooldown chain shift 反向：
          移除 winners 釋放後續 raw signals 中的 SL 觸發）
        - Part B 從 7→3 訊號（移除 2024-07-02, 2024-11-01, 2024-11-18, 2025-09-25
          中的 winners），AI bull regime 中 VXN 持續下降 → 大量 PASS 不及格
        - **核心發現**：NVDA 高品質訊號普遍發生於 VXN 已從近期高點下降的
          「risk-on consolidation」時刻，10d 上升 cap 反向過濾 best signals

Att3（LEVEL cap VXN <= 25，lesson #24 v1 mirror TLT-013 LEVEL dim）：FAILED min 0.41
    參數：use_vxn_direction_filter=False, use_vxn_level_cap=True, max_vxn_level=25
    結果：
        Part A: 16 訊號（vs 26 baseline），WR 68.8%（vs 73.1%），Sharpe **0.41**
                cum +50.08%
        Part B:  6 訊號（vs 7 baseline），WR 83.3%，Sharpe **2.22** cum +46.87%
        min(A,B): **0.41**（-25% vs NVDA-013 baseline 0.55）
    失敗分析：
        - LEVEL cap 過濾 10 Part A 訊號（26→16），其中 7 為 TPs（2020-04-22 VXN 42.37,
          2020-05-28 29.68, 2020-06-15 33.67, 2020-07-16 34.42, 2022-08-08 27.65,
          2022-12-07 28.11, 2023-01-31 25.79, 2023-03-13 29.39, 2023-04-05 24.62…）
        - 4 SLs > 25 也被過濾（35.25, 27.59, 24.93）但其 ratio 不足以彌補 winners 損失
        - WR 同樣下降（73.1%→68.8%）—— 高 VXN regime 在 NVDA 上反而 WR 較高
          （77% vs 低 VXN 67%），cap 過濾移除 high-quality stress-bounce 訊號
        - **核心發現**：NVDA MBPC 在「市場壓力後 NVDA 強勢突破回檔」regime
          表現最好（COVID 後 2020 Q2-Q3 大量高 VXN winners），LEVEL cap 違反
          策略結構性偏好

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================
**結論：lesson #24 forward-looking IV regime gate 結構性失敗於 mega-cap 個股
+ MBPC 框架。三次迭代（DIRECTION 3d cap / DIRECTION 10d cap / LEVEL cap）
全部 REJECT，min(A,B) 退化 5.5% / 69% / 25%。**

1. **Repo 第 5 次 lesson #24 跨資產驗證 — 首次失敗案例**：
   先前 4 次成功皆於 single-driver-IV asset + MR 框架：
   - TLT-013（^MOVE LEVEL，rate-driven，+17%）
   - XLU-013（^MOVE 3d DIRECTION，rate-sensitive utility，+112%）
   - GLD-015（^GVZ 10d DIRECTION，gold safe-haven，+55%）
   - USO-025（^OVX 3d DIRECTION，oil event-driven，+58%）
   NVDA-018 為**首次驗證於 mega-cap 個股**且**首次驗證於 MBPC 框架**，
   兩重邊界擴展同時失敗。

2. **失敗根因分析（雙重邊界）**：
   (a) **Asset 維度 — single-component vs single-driver IV**：^VXN 為 NASDAQ-100
       100 檔成份股 implied vol 加權平均，NVDA 雖為主要權值（~5-12%），但
       單股失敗模式（earnings、guidance、competitive shocks）與 macro NASDAQ
       IV 弱相關。^MOVE 對 TLT 為單一 IV 來源（rates 唯一驅動），^OVX 對 USO
       亦如此（oil 唯一）；^VXN 對 NVDA 為**間接經由整個 NASDAQ-100 中介**。
   (b) **Strategy 維度 — MR vs MBPC 進場結構**：MR 進場期待「IV stress 結束 +
       價格反彈」，IV 上升 → 過濾合理；MBPC 進場期待「突破後淺回檔 + 趨勢
       延續」，IV 與訊號日 forward-looking 預期相關性弱（突破延續訊號的成敗
       由動量持續性決定，而非 IV regime）。

3. **新跨資產規則候選（lesson #24 v3 boundary）**：
   **Forward-looking IV regime gate 適用條件：**
   - **(a) Asset 為 single-driver IV 來源**（rates: ^MOVE, oil: ^OVX, gold: ^GVZ,
     broad equity: ^VIX 對 SPY/IWM 等）— 排除多成份混合的個股
   - **(b) Strategy 為 capitulation MR 框架**（IV stress 為 entry signal 的
     反向過濾器）— 排除 MBPC、breakout 等 trend-continuation 框架
   違反 (a) 或 (b) 任一條件，IV regime gate 結構性失效（NVDA-018 確認）。

4. **NVDA 結構性 Sharpe 上限再次確認 0.55**（NVDA-013 Att3）：
   NVDA-018 為第 14 次實驗、43+ 次嘗試，再度確認多 regime 高波動個股
   （3.26% vol）的策略成熟度天花板。lesson #24 forward-looking IV 為**首次
   negative cross-asset port**，補強 lesson #6 邊界（per-asset structural ceiling
   不可被任意跨資產 lesson 移植所突破）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA018Config(ExperimentConfig):
    """NVDA-018 ^VXN Forward-Looking IV DIRECTION Regime-Gated MBPC 參數"""

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

    # === Multi-week SMA trend regime（lesson #22，同 NVDA-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === ATR vol regime（同 NVDA-013 Att3）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === ^VXN forward-looking implied vol DIRECTION gate（NVDA-018 核心新增）===
    # Att1: lookback=3, max_change=+5.0（XLU-013 / USO-025 sweet spot 直接移植）
    #   → REJECT min 0.52（filter 1 winner 2023-03-13 +5.31，0 SL filtered）
    # Att2: lookback=10, max_change=0.0（longer window，require VXN 不上升）
    # Att3: VXN absolute LEVEL cap（lesson #24 v1 mirror TLT-013 LEVEL dim）
    vxn_ticker: str = "^VXN"
    use_vxn_direction_filter: bool = False
    vxn_direction_lookback: int = 10
    max_vxn_change: float = 0.0
    # LEVEL gate (Att3 only)
    use_vxn_level_cap: bool = True
    max_vxn_level: float = 25.0


def create_default_config() -> NVDA018Config:
    """預設配置（Att1：max_vxn_change=+5.0, lookback=3）"""
    return NVDA018Config(
        name="nvda_018_vxn_implied_vol_mbpc",
        experiment_id="NVDA-018",
        display_name="NVDA ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated MBPC",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
