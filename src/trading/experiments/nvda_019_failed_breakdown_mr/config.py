"""
NVDA-019: Failed Breakdown Reversal Mean Reversion (FBR-MR)

策略方向（Strategy Direction）：
    repo 首次將 Failed Breakdown Reversal（FBR，又稱 "spring" / "bear trap"）
    模式作為 MR 主進場訊號於 NVDA。

    Failed Breakdown 的定義：
        過去 N 個交易日內，價格的 Low 曾跌破 Donchian Lower(M) 支撐
        （Low <= rolling_min(Low.shift(1), M)），但訊號日的收盤價已重新
        站回該 Donchian Lower 之上（Close > Donchian Lower）。
        此模式代表「賣壓已驗證但失敗」，多頭重新奪回支撐。

跨資產 / 跨策略動機（Motivation）：
    1. NVDA-013 Att3（Multi-Week Regime-Aware MBPC）為 NVDA 全域最優（min 0.55）
       但 Part A Sharpe 0.55 與 Part B 2.44 落差高達 4.4 倍，顯示 Part A 為
       強約束。前 18 次實驗已飽和探索 BB Squeeze / RSI extreme / RS / MBPC /
       SMA & vol regime / capitulation depth / oscillator hook / forward IV
       / sector context confirmation 等方向（NVDA-014 ~ NVDA-018 全部失敗
       或僅 PARTIAL）。

    2. **Failed Breakdown Reversal 為 repo 較少使用的 MR 主訊號方向**：
        - lesson #20a 只列出 Failed Breakdown Reversal 在 FXI-009 / 其他
          資產上失敗的紀錄，但 **NVDA 從未測試**。
        - 與 RSI(2) extreme oversold / Pullback+WR / BB Lower touch / Gap-Down
          + intraday reversal 等既有 MR 模式結構不同：
            (a) 不依賴 oscillator turn-up（lesson #20b 失敗家族）
            (b) 不依賴單日 close-position 反轉（lesson #6 邊界）
            (c) 不依賴 N 日累計報酬深度（lesson #19 family）
        - 訊號結構為「先驗證賣壓存在（價格已實際跌破支撐）+ 即時驗證
          賣壓失敗（收盤站回）」雙重條件，理論上比 oscillator hook 更
          可靠，因 oscillator hook 僅是 "soft" 反彈訊號。

    3. **應用於 NVDA 的合理性假設**：
        NVDA 為高 vol（3.26%）AI 龍頭個股，2024-2025 AI 牛市中多次出現
        快速 V-shape 復原（2024-04 修正、2024-08 yen carry trade unwind、
        2025-01 DeepSeek shock 等），符合 "false breakdown → V-bounce"
        模式。但 NVDA-013 Att3 透過 SMA(20)≥SMA(60) trend regime + ATR
        vol regime 已完整防護 2022 deep bear，可直接移植此雙重 regime
        作為 FBR 模式的 quality gate。

策略類型（Strategy Type）：
    均值回歸（Mean Reversion）+ Multi-Week Regime Filter
    （結構性區別於 NVDA-001/-005/-010/-011 既有 NVDA MR 嘗試）

================================================================================
進場條件（Entry Conditions, all must hold on signal day T）
================================================================================
1. 過去 breakdown_lookback_days 個交易日內（含今日），曾發生 breakdown：
       Low_t <= Donchian_Lower_t（其中 Donchian_Lower_t = min(Low) of past
       donchian_period 天，不含今日）
2. 今日收盤站回支撐：Close > Donchian_Lower
3. 今日為陽線：Close > Open（intraday reversal confirmation）
4. 多週期趨勢 regime（lesson #22）：
       SMA(sma_regime_short) >= sma_regime_ratio_min × SMA(sma_regime_long)
5. 多週期波動 regime（lesson #22 cross-strategy from NVDA-013）：
       ATR(atr_regime_short) <= vol_regime_max_ratio × ATR(atr_regime_long)
6. 冷卻 cooldown_days 個交易日

================================================================================
出場條件（Exit Conditions, 含成交模型）
================================================================================
- TP +6% / SL -5% / holding 15 days
- 進場：訊號日收盤偵測 → 隔日開盤市價（含 0.15% 滑價）
- 止盈：Day limit order，盤中 High >= TP 以 TP 成交
- 停損：GTC stop-market，盤中 Low <= SL 以 SL+滑價成交
- 同根 K 線 stop+target 同時觸發 → 悲觀認定（停損優先）
- 到期：隔日開盤市價（含滑價）

================================================================================
基準對照（Baseline: NVDA-013 Att3 全域最優）
================================================================================
- Part A: 26 訊號, WR 73.1%, 累計 +139.54%, Sharpe 0.55
- Part B:  7 訊號, WR 85.7%, 累計  +58.62%, Sharpe 2.44
- min(A,B) 0.55（Part A 為約束）
- 年化 cum diff 26.4%（< 30% ✓），訊號比 1.49:1（< 50% ✓）

驗收目標（Acceptance Criteria）：
    1. min(A,B) > 0.55（NVDA-013 Att3 全域最優）
    2. A/B 年化累積報酬差 < 30%
    3. A/B 年化訊號比 < 50% gap
    4. 使用成交模型（execution model）✓（已內建）

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（baseline FBR + NVDA-013 strict regime gates）：FAILED min(A,B) 0.22
    參數：donchian=20, breakdown_lookback=5, SMA(20)≥1.00×SMA(60),
          ATR(20)≤1.40×ATR(60), Close>Open, cd=10, TP+6/SL-5/15d
    結果：
        Part A: 15 訊號, WR 60.0%, 累計 +22.38%, Sharpe **0.28**
        Part B:  7 訊號, WR 57.1%, 累計  +7.76%, Sharpe **0.22**
        min(A,B): **0.22**（vs NVDA-013 Att3 0.55，**-60%** 嚴重劣化）
    失敗分析：
        - Part A 6 SLs 集中於 macro shock 日（2019-04-29 Q1 earnings、
          2019-05-14 trade war、2019-08-07 yuan deval、2022-01-06 Fed pivot、
          2022-04-13 bear continuation、2022-12-23 hawkish Fed），全為 1-7 天
          快速 SL — failed breakdown 訊號發生於「下跌中段技術性反彈」而非
          true bottom，後續續跌即觸發 SL
        - Part B 3 SLs（2024-04-10 Apr correction、2024-07-22/2024-08-06
          yen carry trade unwind）皆為「第一日反彈」陷阱，1-5 天即 SL
        - SMA(20)≥SMA(60) 與 ATR(20)≤1.40×ATR(60) regime gate **無法分辨**
          「事件驅動單日 V-bounce」與「持續下跌中的 dead cat bounce」
        - 結論：FBR 對 NVDA 高 vol 個股**結構性無區分力**——signal trigger
          在「Low ≤ Donchian Lower 但 Close 站回」此狹義條件下，winners 與
          losers 在價格行為層面幾乎無視覺差異

Att2（+ breakdown depth >= 5% + 收緊 ATR regime 至 1.30）：FAILED min(A,B) -0.01
    參數調整：min_breakdown_depth 0 → 0.05、vol_regime_max_ratio 1.40 → 1.30
    結果：
        Part A: 11 訊號, WR 45.5%, 累計  -2.49%, Sharpe **-0.01**
        Part B:  6 訊號, WR  0.0%, 累計 -27.14%, Sharpe **0.00**
        min(A,B): **-0.01**（**雙向災難**：Part A 退化、Part B 全敗）
    失敗分析：
        - **反直覺發現**：要求更深的 breakdown depth (≥5%) 反而選出**下跌延續**
          訊號而非「孤立 capitulation」。NVDA 高 vol 個股的 5%+ 深度跌破
          往往發生於**真實 bear regime 中段**（2022 整年），而非「單日 V-bounce
          後即將反轉」的情境
        - Part B 6 訊號全敗（0%/6L）—— Att2 移除了 Att1 的所有 4 winners
          並保留 3 losers + 引入 3 新 losers，**完全反向選擇**
        - 收緊 ATR regime（1.40→1.30）並未幫助：NVDA 的 V-bounce 多發生於
          ATR 上升段而非下降段，1.30 上限過嚴反而過濾真實反轉訊號
        - 整合教訓擴展 lesson #19 family 邊界：「signal-day filter 維度（depth）
          在高 vol 個股 FBR 框架中**反向選擇**——深度大者非品質高者」

Att3（還原 Att1 baseline + 加入「Close > 昨日 High」強勢突破確認）：FAILED min(A,B) 0
    參數調整：min_breakdown_depth 0.05 → 0、vol_regime_max_ratio 1.30 → 1.40、
              require_close_above_prev_high False → True
    結果：
        Part A: 13 訊號, WR 61.5%, 累計 +21.71%, Sharpe **0.31**
        Part B:  6 訊號, WR  0.0%, 累計 -27.14%, Sharpe **0.00**
        min(A,B): **0.00**（Part A 略改善但 Part B 全敗）
    失敗分析：
        - **再次反直覺發現**：要求今日 Close > 昨日 High（強勢動能突破）
          反而**保留全部 dead-cat bounces 並過濾真實 V-bounces**
        - 機制：legitimate V-bounces 的反彈日常為「漸進式」收盤強度（today
          Close 在昨日 H/L 區間內或剛超過昨日 Open），不一定突破昨日 High；
          反觀 dead-cat bounces 因短時間爆發式買盤推升價格，當日 Close
          確實常突破昨日 High，但隔日續跌
        - Part B 4 winners（2024-04-25/2024-11-27/2025-09-02/2025-11-24）
          全部被 Close>PrevHigh 過濾；3 losers + 3 新 losers 進入
        - 證實「強勢突破」維度在 NVDA FBR 框架中與 winner/loser 無對齊性

================================================================================
失敗結論（Failure Conclusion）
================================================================================
Failed Breakdown Reversal 模式作為 MR 主訊號於 NVDA（3.26% vol 高 vol AI 個股）
**結構性失敗**。三次迭代全部劣於 NVDA-013 Att3 baseline 0.55：

1. Att1 baseline FBR：min 0.22（-60%）
2. Att2 + breakdown depth filter：min -0.01（-102%，雙向災難）
3. Att3 + close>prev_high filter：min 0.00（Part B 6/0% 全敗）

**核心失敗根因**：
1. **訊號定義不可行於高 vol**：NVDA 的 Donchian Lower 在持續下跌中持續下移，
   每天都可能 trigger「Low ≤ Donchian Lower」+「Close > Donchian Lower」
   並滿足「Close > Open」陽線條件，因此 FBR 訊號**幾乎無篩選力**
2. **Signal-day filter 維度反向選擇**：depth filter 與 prev-high filter
   皆**反向選擇 winners**——高 vol 個股 false breakdowns 與 true bottoms
   在 signal-day 層面行為相似（同樣是「跌破又拉回」），但跨多天的軌跡不同
3. **Lesson #20a 失敗家族擴展**：repo 既有 FXI-009 Failed Breakdown Reversal
   失敗，**NVDA-019 為 repo 第 1 次將 Failed Breakdown Reversal 應用於高 vol
   個股 + MR 框架**，雙重失敗（high-vol single stock + MR primary entry）。
   擴展 lesson #20a：「Failed Breakdown Reversal 不適用於 (a) 政策驅動 EM ETF
   (FXI)、(b) 高 vol mega-cap 個股 (NVDA)」

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================
1. **repo 第 1 次將 Failed Breakdown Reversal 作為 MR 主訊號於高 vol 個股**：
   FXI-009 為 repo 唯一既有 FBR 試驗（政策驅動 EM ETF，亦失敗）。NVDA-019
   擴展失敗家族至高 vol mega-cap 個股 + MR 框架。

2. **Lesson #19 family v13 反向選擇邊界**：signal-day depth filter（Att2 5%）
   在 NVDA FBR 框架反向選擇 winners——深度大反而是下跌延續而非孤立反彈。
   與 NVDA-011（capitulation depth）+ NVDA-017（5d return ceiling）並列為
   NVDA signal-day filter 三次失敗（lesson #19 family 在 NVDA 高 vol 結構
   完全失效）。

3. **NVDA 結構性 Sharpe 上限再度確認**：NVDA-013 Att3 min 0.55 仍為全域最優
   （19 次實驗、43+ 次嘗試）。NVDA-014~019 連續 6 次失敗強化「entry-side
   exploration 已飽和」——後續嘗試應集中於 (a) exit optimization、(b) ATR
   ratio BAND（CIBR-014 路徑）、(c) macro context confirmation 進一步精煉。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA019Config(ExperimentConfig):
    """NVDA-019 Failed Breakdown Reversal MR 參數"""

    # === Failed Breakdown Reversal 主訊號 ===
    donchian_period: int = 20  # Donchian Lower lookback
    breakdown_lookback_days: int = 5  # 多少日內曾發生 breakdown
    require_bullish_close: bool = True  # 今日 Close > Open

    # === Att2 試驗（已棄用）：breakdown 深度過濾 ===
    # breakdown_depth = (Close - min(Low) over breakdown_lookback_days) / Close
    # Att2 試驗將其設為 0.05 但失敗：深度大者反為下跌延續，非孤立 capitulation
    min_breakdown_depth: float = 0.0  # 預設停用

    # === Att3 新增：強勢收盤確認 ===
    # 今日 Close > 昨日 High，要求真實 day-over-day 突破動能
    require_close_above_prev_high: bool = False

    # === 多週期趨勢 regime（lesson #22，同 NVDA-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 多週期波動 regime（lesson #22 cross-strategy，同 NVDA-013 Att3）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === 冷卻期 ===
    cooldown_days: int = 10


def create_default_config() -> NVDA019Config:
    """建立預設配置（保留 Att1 baseline，三次迭代全部 REJECT，最終為失敗實驗，
    Att1 為 min(A,B) 0.22 最不差的一次嘗試）"""
    return NVDA019Config(
        name="nvda_019_failed_breakdown_mr",
        experiment_id="NVDA-019",
        display_name="NVDA Failed Breakdown Reversal Mean Reversion",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.06,
        stop_loss=-0.05,
        holding_days=15,
        # Att1 baseline（三次迭代中最不差的一次）
        min_breakdown_depth=0.0,
        vol_regime_max_ratio=1.40,
        require_close_above_prev_high=False,
    )
