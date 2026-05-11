"""TQQQ-022: QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation Buy

策略方向（Strategy Direction）：
    Cross-asset Pair Divergence FLOOR Regime Gate（lesson #20 v3 / lesson #19
    family v3 / lesson #26 family v2 cross-asset divergence regime gate 應用）。

    在 TQQQ-018 Att3（Volatility-Regime-Gated Capitulation Buy + first-day-of-
    decline filter，min(A,B) 0.80，全域最優）基礎上，疊加 **QQQ - SPY 20 日報酬差
    FLOOR 過濾**——過濾「tech 顯著跑輸 broad market」的 tech-specific 結構性
    弱勢 regime。

    **Repo 首次將 cross-asset divergence regime gate 移植至**：
    (a) 槓桿 ETF（3x leveraged tech ETF）+ extreme capitulation framework
    (b) 使用底層追蹤指數（QQQ）vs broad market（SPY）作為 anchor，避免槓桿
        ETF 自身波動扭曲 divergence 訊號

    既有 cross-asset divergence regime gate 成功案例（lesson #20 v3 family）：
        - TLT-014 (TLT-SPY 20d FLOOR, 利率資產 vs 股票)
        - TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤科技)
        - NVDA-021 (NVDA-QQQ 20d CEILING, 高波動 AI 個股 vs 大盤科技)
        - INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM)
        - EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM)
        - EWT-010 (EWT-EEM 2D 20d/60d CEILING)
        - FXI-015 (FXI-ASHR 20d FLOOR, China ETF onshore vs offshore)
        - GLD-016 (GLD-DXY 5d FLOOR, gold vs USD)

跨資產移植動機（Cross-Asset Port Motivation）：
    TQQQ-018 Att3 殘存 SLs：
    - Part A: 1 SL (2021-09-28，BB 0.219、DD_5d_ago -12.57%) — 低 vol regime
      drift SL，doc 中標記「結構性無法以任何技術維度過濾」
    - Part B: 1 SL (2025-03-06，Trump 關稅公告期) — 對應 BB 0.477、Vol regime
      閘門通過，prior DD 也通過

    **核心假說（QQQ-SPY Tech Structural Weakness FLOOR Hypothesis）**：
        TQQQ 進入極端 capitulation（DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x +
        BB width regime gate + DD(T-5) ≤ -1%）時，若同時出現 QQQ 過去 20 日
        報酬顯著跑輸 SPY（QQQ_20d - SPY_20d 深度負向），代表此波下跌為
        tech-specific 結構性弱勢（如 2025-03-06 關稅公告對科技類股加重打擊、
        2021-09 Fed 鷹派態度對科技 multiple 壓抑），bounce 概率低於兩者同步
        下跌的 broad-market panic 場景；前者 mean-reversion 失效率較高，後者
        更接近真正的 capitulation buy 機會。
        相對地，當 QQQ - SPY 20d divergence ≥ FLOOR threshold，TQQQ 的下跌
        屬於 broad-market 同步 panic，capitulation buy 高品質訊號不被過濾。

    與 lesson #5「趨勢濾波器+均值回歸=災難」的明確區分：
        - lesson #5 警告針對 same-asset trend filter on MR（如 SPY SMA200 用作
          MR 進場濾波器）
        - 本實驗：(a) 進場為 capitulation buy（不是 trend pullback MR）、
          (b) divergence 為「跨資產 multi-week relative performance regime
          classifier」而非 TQQQ 自身方向過濾、(c) anchor 為 QQQ vs SPY
          relative performance，非 TQQQ 自身趨勢
        - 沿用 TLT-014 / TSLA-017 / NVDA-021 cross-asset divergence regime
          gate 的合法性論證

    Anchor 選擇（QQQ vs SPY）的設計理由：
        - QQQ 為 TQQQ 直接追蹤標的（1x），SPY 為 broad market benchmark
        - 不使用 TQQQ vs SPY：TQQQ 3x 槓桿放大波動，會扭曲 20d divergence 訊號
          （同樣的 QQQ-SPY 跑輸幅度，TQQQ 會顯示 3x 倍率，閾值校準困難）
        - QQQ vs SPY 提供乾淨的「tech 板塊 vs broad market」相對表現訊號

    與 TQQQ-019 / TQQQ-020 / TQQQ-021（已驗證 implied vol 維度全部失敗）的區分：
        - TQQQ-019/020/021：^VIX 5d direction、^VIX 1d peak-passing、^MOVE
          LEVEL/DIRECTION — 全部 implied vol 維度，與 TQQQ extreme capitulation
          結構性共線或非綁定
        - TQQQ-022：cross-asset relative performance 維度，**非 implied vol**，
          直接對應 AI_CONTEXT 中明確列出的「未驗證假設」之一：「cross-asset
          relative strength（如 TQQQ vs SPY 相對強度）」

策略類型：恐慌抄底 + 波動率 regime + first-day filter + 跨資產相對表現 regime gate
    （Capitulation Buy + Vol Regime + Transition Filter + Cross-Asset Divergence Filter）

================================================================================
基礎（同 TQQQ-018 Att3）
================================================================================
- DD ≤ -15%（從 20 日高點）
- RSI(5) < 25
- Volume > 1.5 × SMA(20)
- BB(20, 2) Width / Close < 0.48（vol regime gate）
- DD(T-5) ≤ -1%（first-day-of-decline filter）
- 冷卻 3 日
- TP +7% / SL -8% / 10 天，0.1% 滑價

================================================================================
TQQQ-022 新增（lesson #20 v3 cross-asset divergence FLOOR）
================================================================================
- **QQQ 20 日報酬 - SPY 20 日報酬 ≥ min_relative_return**
- Att1: min_relative_return = -0.05（-5%，loose floor，僅過濾極端 tech 弱勢）
- Att2: min_relative_return = -0.03（-3%，moderate floor）
- Att3: min_relative_return = -0.015（-1.5%，tighter floor，目標精準切除 SLs）

================================================================================
基準對照（TQQQ-018 Att3 全域最優，2026-04-28）
================================================================================
- Part A: 10 訊號, WR 90.0%, 累計 +68.97%, Sharpe 1.21, MDD -9.07%
- Part B:  6 訊號, WR 83.3%, 累計 +28.91%, Sharpe 0.80
- min(A,B) 0.80
- A/B 年化 cum diff: 18.1%（< 30% ✓），訊號比 1.5:1（gap 33% < 50% ✓）

驗收目標：min(A,B) > 0.80，維持 A/B 平衡（cum diff < 30%, signal gap < 50%）。

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1 (lookback=20d, min_relative_return=-0.03 moderate)：REJECT min(A,B) **0.39**
    結果：
        Part A: 7 訊號, WR 71.4%, 累計 +18.48%, Sharpe **0.39**, MDD -9.85%
        Part B: 6 訊號（不變）, WR 83.3%, 累計 +28.91%, Sharpe **0.80**
        min(A,B): **0.39**（**-51% vs TQQQ-018 Att3 baseline 0.80**）
    失敗分析：
        - Part A reverse selection：訊號 10→7（-3 winners），WR 90.0%→71.4%（-18.6pp）
        - filter 額外保留 1 SL（2021-09-28，QQQ-SPY 20d 在 -3% 之上通過）
        - Part B 完全不變（5 winners + 1 SL 全部通過 -3% 門檻），2025-03-06 SL
          QQQ-SPY 20d 結構性 ≥ -3%，filter 對該 SL 無區分力

Att2 (lookback=20d, min_relative_return=-0.05 loose floor，threshold robustness)：
    TIE baseline，Part A 略劣化
    結果：
        Part A: 9 訊號, WR 88.9%, 累計 +57.92%, Sharpe **1.12**（vs baseline 1.21, -7%）
        Part B: 6 訊號（不變）, WR 83.3%, 累計 +28.91%, Sharpe **0.80**
        min(A,B): **0.80**（TIE baseline，Part B 為 binding constraint）
    失敗分析：
        - -5% 為 loose floor，Part A 訊號 10→9（移除 1 winner，QQQ-SPY 20d 介於
          [-5%, -3%]）；其餘 9 訊號（含 1 SL 2021-09-28）QQQ-SPY 20d ≥ -5%
        - Part B 完全不變（所有 6 訊號 QQQ-SPY 20d ≥ -5%）
        - 2025-03-06 SL QQQ-SPY 20d ≥ -5%（即使 tariff 衝擊 tech，broad market
          同步下跌使 20d divergence 未達深度負向）
        - **threshold 沒有 sweet spot**：-3% 損害 Part A、-5% 略損 Part A 但 Part B
          均無改善，搜尋空間整體無解

Att3 (lookback=10d, min_relative_return=-0.03 acute event shock 維度)：REJECT min **0.66**
    結果：
        Part A: 6 訊號, WR 83.3%, 累計 +28.91%, Sharpe **0.80**
        Part B: 5 訊號, WR 80.0%, 累計 +20.48%, Sharpe **0.66**
        min(A,B): **0.66**（**-18% vs baseline 0.80**）
    失敗分析（最劣迭代）：
        - 10d 縮短 lookback 加劇 reverse selection
        - Part A 訊號 10→6（-4 winners，仍保留 1 SL 2021-09-28）
        - Part B 訊號 6→5（-1 winner 2024-07-24，仍保留 1 SL 2025-03-06）
        - 10d 急性窗口本應對 tariff 等急性衝擊更敏感，但實際 QQQ-SPY 10d 在
          tariff 期間（2025-03-06 前 10d）並非顯著負向（broad market 同步下跌）

================================================================================
最終結論：QQQ-SPY Cross-Asset Divergence FLOOR 對 TQQQ extreme capitulation
framework 結構性失敗
================================================================================

**核心失敗模式（lesson #20 v3 family v11 邊界擴展，repo 首次發現）**：
1. **TQQQ extreme capitulation 與 QQQ-SPY divergence 結構性脫鉤**：
   - TQQQ-018 框架要求 DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x，此類訊號天然
     發生於 broad-market panic 期（COVID、Fed pivot、Trump tariff 等），QQQ
     與 SPY 通常同步下跌，20d/10d divergence 不顯著
   - Tech-specific 結構性弱勢期（如 2022 Fed 加息 tech 跑輸）已被 BB-width
     regime gate（< 0.48）過濾，剩餘訊號天然落於 broad-market 同步 panic 區

2. **Reverse selection 嚴重**：
   - Part A 10 winners + 1 SL 中，winners 集中於 QQQ-SPY 20d ∈ [-5%, -1%]，SL
     2021-09-28 的 QQQ-SPY 20d ≥ -1%（low vol regime drift 期 tech 與 broad
     同步弱勢，divergence 微弱），任何 FLOOR threshold 移除 winners 多於 SL
   - Part B 5 winners + 1 SL 中，2025-03-06 SL 的 QQQ-SPY 20d ≥ -3%（tariff
     初期 broad market 同步下跌，divergence 未深化）

3. **Repo 第 X 次「broad-vs-broad 對稱類別」cross-asset divergence 失敗驗證**：
   - 既有 broad-vs-broad 失敗：EEM-017（EEM-EFA 廣 EM vs 廣 DM）
   - TQQQ-022（QQQ vs SPY 廣科技 vs 廣大盤）為新失敗案例
   - 雖 NVDA-021（NVDA-QQQ）+ TSLA-017（TSLA-QQQ）成功，但 anchor 為**個股 vs
     廣科技**，TQQQ-022 為**廣科技 vs 廣大盤**結構不同

4. **新跨資產規則（lesson #20 v3 v11 邊界精煉）**：
   - cross-asset divergence regime gate 適用結構 = 「target 為 narrower scope
     vs broader benchmark」+「target SLs 在 divergence 維度有方向性集中」
   - **「underlying ETF + leveraged ETF」共生組合上的 underlying-vs-broader
     divergence 失敗**：QQQ ≈ TQQQ 的 underlying，QQQ-SPY divergence 反映
     QQQ 板塊 vs 大盤狀態，但 TQQQ extreme capitulation 訊號日已被 vol
     regime gate（BB width）過濾，剩餘訊號集中於 broad panic regime（QQQ ≈
     SPY 同步），divergence 維度自然壓縮

5. **TQQQ Part B 0.80 binding ceiling 仍無法突破**：
   - 已試 implied vol（TQQQ-019/020/021）+ cross-asset relative strength
     （TQQQ-022）兩大維度全失敗
   - AI_CONTEXT 中剩餘未驗證假設：「underlying QQQ short-term momentum
     reversal」、「yield curve slope velocity」（TLT-017 成功維度）
   - 或「完全替代 framework」（vol-transition MR / BB Squeeze）
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ022Config(TQQQ018Config):
    """TQQQ-022 QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation 參數"""

    # === QQQ-SPY Cross-Asset Divergence FLOOR（TQQQ-022 核心新增）===
    # 訊號通過條件：QQQ 20d 報酬 - SPY 20d 報酬 >= min_relative_return
    # （FLOOR 方向：過濾 QQQ 已顯著跑輸 SPY 的 tech-specific 結構性弱勢 regime）
    qqq_ticker: str = "QQQ"
    spy_ticker: str = "SPY"
    # Att2 為三次迭代最佳（TIE baseline，僅 -7% Part A Sharpe 退化），保留為預設
    # 整體實驗失敗：QQQ-SPY divergence 為 reverse-selection 維度於 TQQQ-018 框架
    divergence_lookback: int = 20
    # Att1: 20d, -0.03（moderate）→ Part A 7/71.4%/0.39, Part B 6/83.3%/0.80, min 0.39 REJECT
    #   reverse selection（移除 winners 而非 SLs，2025-03-06 Part B SL 通過 -3% 門檻）
    # Att2: 20d, -0.05（loose floor）→ Part A 9/88.9%/1.12 cum +57.92%（-7% vs baseline 1.21）
    #   Part B 6/83.3%/0.80 unchanged / min 0.80 TIE baseline，僅移除 1 winner 不影響 SL
    # Att3: 10d, -0.03（acute event shock 維度，REJECT）→ Part A 6/83.3%/0.80 / Part B
    #   5/80.0%/0.66 / min 0.66（**最差迭代**，10d 維度 reverse selection 加劇）
    min_relative_return: float = -0.05
    use_divergence_filter: bool = True


def create_default_config() -> TQQQ022Config:
    """預設配置（Att2 moderate floor，後續依結果迭代）"""
    return TQQQ022Config(
        name="tqqq_022_qqq_spy_divergence_cap",
        experiment_id="TQQQ-022",
        display_name="TQQQ QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation Buy",
        tickers=["TQQQ"],
        data_start="2018-06-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
    )
