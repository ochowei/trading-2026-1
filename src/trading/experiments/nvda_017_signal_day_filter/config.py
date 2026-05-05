"""
NVDA-017: Signal-Day 5d Return CEILING on Multi-Week Regime-Aware MBPC
            (Lesson #19 family v10/v12 cross-asset port from TSM-011 Att3 -
             repo first MBPC framework application)

策略方向（Strategy Direction）：
    在 NVDA-013 Att3（Multi-Week Regime-Aware MBPC，min(A,B) 0.55 全域最佳）
    基礎上，疊加**訊號日 5 日報酬 CEILING（rally exhaustion 過濾器）**，
    嘗試解決「淺回檔但前段已大漲導致延續失敗」的 SL 結構。

跨資產移植動機（Cross-Asset Port from TSM-011 Att3）：
    TSM-011 Att3（5d ceiling +10.5%）為 repo 首次 lesson #19 family
    cross-strategy 鏡像擴展（MR FLOOR → momentum CEILING），於 TSM-008
    RS Momentum Pullback 框架成功（min(A,B) 0.79 → 0.83）。

    TSM-011 跨資產假設明列：「rally exhaustion 5d ceiling 適用於其他 RS /
    MBPC 動量框架（NVDA-006 RS / VOO-004 MBPC / SOXL-010 RS / EWT-008 等），
    閾值依資產 5d return 分布調整」。

    NVDA-017 為**首次將 TSM-011 假設移植至 MBPC 框架**（非 RS 框架，與
    NVDA-006 RS 平行候選但選擇較高 baseline 的 NVDA-013 為基礎以追求
    結構性 Sharpe 上限再突破）。

================================================================================
NVDA-013 Att3 Trade-Level 5 日報酬分析（pre-experiment research）
================================================================================
Part A 7 SLs 訊號日 5d 分布：
    2019-02-20 SL: 5d **+4.88%** （最高 5d，唯一突破 max TP 5d）
    2020-10-20 SL: 5d -4.23%
    2021-02-18 SL: 5d +0.44%
    2021-04-21 SL: 5d +0.55%
    2022-04-04 SL: 5d -3.04%
    2023-07-25 SL: 5d -3.82%
    2023-08-28 SL: 5d -0.28%

Part A 17 TPs + 2 EXPs 訊號日 5d 分布：
    最高 5d: 2020-06-15 TP +4.19%
    其餘 TPs 5d 多為負（淺回檔本質上 5d 略負屬常態）

Part B 7 訊號日 5d 分布：
    最高 5d: 2025-10-13 TP +1.50%
    Part B 全部 5d <= +1.5%，遠低於任何 ceiling 候選閾值

設計理論預測：
- 唯一 5d > +4.5% 的訊號為 2019-02-20 SL
- max Part A TP 5d 為 +4.19%（2020-06-15）
- 設計甜蜜邊界 ret_5d_max = +4.5%（surgical 過濾 1 SL，保留全部 TPs/Part B）

================================================================================
迭代結果（Iteration Log）
================================================================================
Att1 ★（預測甜蜜點）: ret_5d_max = 0.045 — FAILED min(A,B) 0.52
    結果：
        Part A: 25 訊號 / WR 72.0% / Sharpe **0.52** cum **+121.80%**
                （vs baseline 26/73.1%/0.55/+139.54%）
        Part B: 7 訊號 / WR 85.7% / Sharpe 2.44 cum +58.62%（不變）
        min(A,B) **0.52**（-5.5% vs NVDA-013 baseline 0.55）

    失敗根因（lesson #19 cooldown chain shift）：
        - 5d ceiling 4.5% 過濾 2019-02-20 SL（5d +4.88%）—— 預期改善
        - 但**釋放原本被 2019-02-20 cooldown 壓抑的 2019-03-01 raw signal**
          （5d -1.62%，未被 ceiling 過濾）
        - 2019-03-01 fires → 4 trading days SL（-7.14%）
        - 2019-03-01 之 cooldown（10 trading days）反向**壓抑 2019-03-08 TP**
          （+8.00%）
        - 淨效應：-1 SL（filtered）+ 1 SL（unlocked）− 1 TP（locked out）
                = 0 SL 改善 + 1 TP 損失
        - cum 從 +139.54% 降至 +121.80%（淨 -17.74pp）

    結構性問題：NVDA-013 殘餘 SLs 為 heterogeneous failure modes，無單一
    signal-day return 維度 surgical 切點。2019-02-20 SL 與其相鄰 2019-03-01
    raw signal 均缺乏共同 signal-day technical signature——
    2019-02-20: 5d +4.88, 1d +1.22, 3d +2.60, 10d +5.74
    2019-03-01: 5d -1.62, 1d +1.42, 3d -0.31, 10d +1.35
    僅 1d return 有同向（皆正）但其他 TPs/Part B 1d 廣泛分布，
    1d 過濾系統性傷害贏家集合。

Att2（更嚴 ceiling）: ret_5d_max = 0.040 — FAILED min(A,B) 0.52（同 Att1）
    結果：
        Part A: 25 訊號 / WR 72.0% / Sharpe **0.52** cum **+121.80%**（與 Att1 相同）
        Part B: 7 訊號 / WR 85.7% / Sharpe 2.44 cum +58.62%（不變）
        min(A,B) **0.52**（-5.5% vs baseline 0.55，與 Att1 相同）

    失敗分析（second-order cooldown chain shift）：
        - 4.0% ceiling 額外過濾 2020-06-15 TP（5d +4.1880%, +8.00% return）
        - 但此過濾觸發第二次 cooldown chain shift：unleash 2020-06-29 raw signal
          （亦為 +8.00% TP），與被過濾的 2020-06-15 TP 1-for-1 替換
        - 原 Part A 訊號集中 2020-06-15 → 2020-06-29 之 TP 替換淨效應為 0
          （兩者皆 +8.00% TP，cum 維持）
        - 同時保留 Att1 之 2019-02-20 → 2019-03-01 SL chain shift（淨負效應）
        - 結果 25 訊號 / Sharpe 0.52 與 Att1 完全相同，確認 [0.040, 0.045]
          區間為「robust sweet spot of failure」（連續 5d ceiling threshold
          區間皆觸發 chain shift 副作用）

Att3（ablation 寬鬆）: ret_5d_max = 0.050 — ABLATION = baseline 0.55
    結果：
        Part A: 26 訊號 / WR 73.1% / Sharpe **0.55** cum **+139.54%**
        Part B: 7 訊號 / WR 85.7% / Sharpe 2.44 cum +58.62%
        min(A,B) **0.55**（與 NVDA-013 Att3 baseline 完全相同）

    確認：max SL 5d = +4.88% < 0.050，ceiling 非綁定，所有訊號通過 →
    證實 5d ceiling 只在 [0.0420, 0.0488] 邊界內 binding，且該區間中
    cooldown chain shift 結構性破壞 baseline。

================================================================================
最終結論（REJECT 跨資產假設）
================================================================================
**NVDA-017 三次迭代均失敗，REJECT TSM-011 「rally exhaustion 5d ceiling」
跨資產假設於高波動 AI 個股 + MBPC 框架。**

NVDA-013 全域最佳 min(A,B) 0.55 維持。

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================

1. **TSM-011 跨資產假設邊界確認**：lesson #19 family v10/v12 「rally
   exhaustion CEILING」於 RS Momentum 框架（TSM-008）成功，但**結構性失敗
   於高波動多 regime AI 個股 + MBPC 框架**。框架差異：
   - TSM-008 RS：訊號日 5d 分布廣（max SL +11.30%），單一 outlier SL 可
     surgical 過濾；冷卻鏈為「TP 序列」，移除單一 SL 不易觸發 chain shift。
   - NVDA-013 MBPC：訊號日 5d 分布窄（max SL +4.88% / max TP +4.19%，
     gap 0.69%），filter 區間極窄；且 SL 空間異質（7 SLs 分屬多個 regime
     失敗模式：bull rally exhaustion / pre-election vol / yields surge /
     semi correction / bear false rally / top forming），無單一 signal-day
     return 維度可分離。
   - **2019-02-20 SL 過濾觸發 cooldown chain shift**：unleash 2019-03-01
     suppressed signal（5d -1.62%，無共同 ceiling 可同時過濾），系統性
     替換 1 SL + lock-out 1 TP，淨負面。

2. **Cooldown chain shift 邊界擴展**（lesson #19 family）：
   先前 chain shift 案例多為 MR FLOOR 過濾（DIA-012 / GLD-014 等），
   方向多為「過濾 cap 後釋放更深 floor」；NVDA-017 為**第 1 次 momentum
   CEILING 框架觸發 chain shift**，方向為「過濾單 SL 後釋放鄰近 raw SL，
   再 lock-out 後續 TP」。失敗模式對稱於 MR floor chain shift。

3. **NVDA 結構性 Sharpe 上限再次確認**：NVDA-016（broad-market context
   confirmation gate）+ NVDA-017（rally exhaustion ceiling）均失敗，
   累積 17 次實驗 + 50+ 次嘗試後 NVDA min(A,B) Sharpe 0.55 為現有純技術面
   + signal-day filter + cross-asset macro gate 三重維度的結構性上限。
   未來改進方向需脫離既有框架（例如 earnings calendar 季節性過濾、
   forward-looking implied vol BANDS（^VXN）跨資產組合等）。

4. **Heterogeneous SL 結構作為 signal-day filter 適用邊界**：NVDA-013
   的 7 個 Part A SLs 在 1d / 3d / 5d / 10d / 20d / VXN / ATR(5)/ATR(20) /
   ATR(20)/ATR(60) / NVDA-SMH 10d 等 9 個維度上分布廣泛重疊，無單一維度
   surgical 切點。**新跨資產邊界**：signal-day return ceiling 適用條件需
   asset 殘餘 SLs **集中於單一失敗模式**（如 TSM 「post-rally exhaustion」、
   FCX 「3d 急漲」、URA 「5d 持續下挫」），對 multi-regime heterogeneous
   SLs 結構（NVDA-013）系統性失效。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA017Config(ExperimentConfig):
    """NVDA-017 Signal-Day 5d Return Ceiling on MBPC 參數"""

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

    # === NVDA-017 訊號日 5 日報酬 CEILING（rally exhaustion 過濾） ===
    # 三次迭代結果（均 FAIL，REJECT 跨資產假設）：
    #   Att1 (0.045): FAIL min 0.52 — cooldown chain shift（2019-02-20 SL
    #                 過濾後釋放 2019-03-01 raw SL + lock-out 2019-03-08 TP）
    #   Att2 (0.040): FAIL min 0.49 — 額外誤殺 2020-06-15 TP（5d +4.19%）
    #   Att3 (0.050): ABLATION = baseline 0.55（max SL 5d +4.88% < 0.050，
    #                 ceiling 非綁定）
    # 最終配置採 Att3 ablation（非綁定）以保留 baseline 行為作為基準對照
    ret_5d_max: float = 0.050


def create_default_config() -> NVDA017Config:
    """建立預設配置（Att3 ablation：5d ceiling 0.050）"""
    return NVDA017Config(
        name="nvda_017_signal_day_filter",
        experiment_id="NVDA-017",
        display_name=("NVDA Signal-Day 5d Return Ceiling on Multi-Week Regime-Aware MBPC"),
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
