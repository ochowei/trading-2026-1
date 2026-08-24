"""
TSM-010: Multi-Week Regime-Aware Momentum Breakout Pullback Continuation

策略方向（Strategy Direction）：
    將 lesson #22「buffered multi-week SMA trend regime」+ ATR vol regime
    （NVDA-013 cross-strategy success）跨資產移植至 TSM（台積電）的 MBPC
    框架。Repo 第 2 次 lesson #22 + MBPC 跨資產試驗。

動機（Motivation）：
    TSM 已有 9 次實驗，當前全域最優為 TSM-008（RS exit optimization：
    TSM-SMH 20 日 RS≥5% + 5 日回撤 3-7% + Close>SMA(50)，TP+8%/SL-7%/25d）
    Part A Sharpe 0.79 / Part B 0.83 / min(A,B) 0.79，A/B 訊號比 1.2:1。

    TSM-006（Momentum Pullback：ROC(20)≥10% + 5 日回撤 3-7% + SMA(50)，
    TP+7%/SL-7%/20d）為 MBPC 變體基線：min(A,B) 0.46 / A/B 比 1.2:1。

    **lesson #22 + MBPC 跨資產假設**：NVDA-013 已驗證 buffered multi-week
    SMA regime（k=1.00 strict）+ ATR vol regime（≤ 1.40 × ATR(60)）對
    multi-regime 高波動半導體個股有效。TSM 與 NVDA 同為半導體類，日波動
    ~2.1%，預期同類 regime classifier 能精準分隔「真實多週期上升 regime」
    與「late-cycle / chop regime」。

    與既有 TSM 實驗的差異：
    - TSM-005（BB Squeeze Breakout，純突破）：失敗 min 0.16
    - TSM-006（Momentum Pullback，純動量）：min(A,B) 0.46
    - TSM-008（RS Exit Optimization，相對強度框架）：min(A,B) 0.79
    - **TSM-010（lesson #22 + MBPC 雙重 regime gate）**：repo 第 2 次
      lesson #22 + MBPC 試驗、首次 TSM 上 cross-strategy 移植

策略類型：趨勢跟蹤 / 動量延續 + 多週期 regime gate
    （Trend-following / Momentum Continuation + Multi-Week Regime Filter）

================================================================================
基礎（同 NVDA-013 / NVDA-009 baseline）
================================================================================
- Donchian 20 日新高，breakout freshness ≤ 10 日
- Close > SMA(50)
- 5 日高點回檔 ∈ [-3%, -8%]
- RSI(14) ∈ [40, 65]
- Close > Open（多頭 K 棒）
- 冷卻 10 日
- TP +8% / SL -7% / 20 天，0.15% 滑價（半導體個股 NVDA-013 直接移植）

================================================================================
TSM-010 新增（lesson #22 + ATR vol regime + 2DD cap）
================================================================================
- **多週期趨勢 regime**：SMA(20) ≥ 1.00 × SMA(60)（k=1.00 strict）
- **多週期波動 regime**：ATR(20) ≤ 1.40 × ATR(60)（NVDA-013 Att3 設定）
- Att3 新增 **2DD cap**（lesson #19 family）：2 日報酬 >= -2%（嚴格過濾
  signal day 加速下跌訊號）

================================================================================
基準對照（TSM-008，當前全域最優）
================================================================================
- Part A: 12 訊號, Sharpe 0.79
- Part B: 10 訊號, Sharpe 0.83
- min(A,B) 0.79, A/B 訊號比 1.2:1

驗收目標：min(A,B) > 0.79（TSM-008 全域最佳），維持 A/B 平衡（cum diff
< 30%、訊號比差距 < 50%）。

================================================================================
迭代歷程（Iteration Log）— 三次迭代全部失敗 vs TSM-008 min 0.79
================================================================================
Att1（NVDA-013 Att3 直接移植：k=1.00 + ATR ≤ 1.40 + recency 10d
      + pullback [-3%,-8%] + RSI [40,65]）：FAILED min(A,B) 0.03
    結果：
        Part A: 19 訊號, WR 47.4%, 累計 -0.06%, Sharpe **0.03**
        Part B: 12 訊號, WR 58.3%, 累計 +18.33%, Sharpe **0.23**
        min(A,B): **0.03**（vs TSM-008 baseline 0.79 嚴重退化）
    失敗分析：
        - Part A 19 訊號中 8 SLs 散佈於多 regime（2019-04 trade war、
          2020-01 pre-COVID、2020-09、2021-02、2022-08、2022-12、2023-03、
          2023-07）—— 與 NVDA Part A 11 SLs 同樣多 regime 分布，但 TSM
          WR 僅 47.4% vs NVDA 73.1%
        - 根因：TSM Part A 包含 **更多 regime（4+）** vs NVDA 3 regimes：
          (a) 中國地緣政治風險（trade war、中美科技戰）
          (b) COVID 市場震盪
          (c) AI hype / correction（半導體上下游連動）
          (d) 半導體產業週期（記憶體、晶圓代工景氣）
        - lesson #22 SMA regime + ATR vol regime 雙重 gate 對 TSM 多
          regime SLs **缺乏選擇性**，原因為 TSM SLs 多發生於 SMA20/SMA60
          仍 > 1.00 + ATR 仍正常的「短暫地緣政治震盪 / 產業景氣轉折」期間

Att2（VOO-004 Att3 方向：recency 5d + pullback [-2%,-5%] 收緊）：
      FAILED min(A,B) -0.10
    參數調整：
        - breakout_recency_days 10 → 5
        - pullback_min -0.03 → -0.02
        - pullback_max -0.08 → -0.05
    結果：
        Part A: 13 訊號, WR 46.2%, 累計 -11.10%, Sharpe **-0.10**
        Part B: 5 訊號, WR 60.0%, 累計 +8.62%, Sharpe **0.26**
        min(A,B): **-0.10**（三次最差）
    失敗分析：
        - 收緊進場條件後 Part A 訊號 19→13（-32%）但 WR 47.4%→46.2%
          幾乎不變 → 過濾為**非選擇性**，移除 winners 與 losers 比例相當
        - 與 VOO-004 Att3 對比：VOO 上 tight→loose 翻轉 0.12→1.12（+833%
          Sharpe）顯示 VOO 訊號帶在 tight 區間；TSM 上 tight 區間訊號
          分布**反向**——tight 區間更多 SLs，loose 區間有更多 winners
        - **新跨資產發現（lesson #4 反例擴展）**：進場敏感度方向取決於
          資產 multi-regime 結構——VOO 單一 uptrend regime 中 tight
          捕捉純動能訊號；TSM multi-regime 中 tight 反而捕捉「短暫
          regime 突破中的假動量」訊號

Att3（恢復 NVDA-013 預設 + 新增 2DD cap >= -2%，lesson #19 cap 方向）：
      FAILED min(A,B) 0.08
    參數調整：
        - 還原 breakout_recency=10, pullback [-3%, -8%], RSI [40, 65]
        - 啟用 use_dd2_cap=True, dd2_cap_threshold=-0.02（嚴格 2DD cap）
    結果：
        Part A: 14 訊號, WR 50.0%, 累計 +4.75%, Sharpe **0.08**
        Part B: 12 訊號（不變）, WR 58.3%, 累計 +18.33%, Sharpe **0.23**
        min(A,B): **0.08**（vs Att1 0.03 邊際改善 +0.05，仍遠不及 TSM-008
        baseline 0.79）
    失敗分析：
        - 2DD cap 過濾 5 訊號（19→14），WR 從 47.4%→50.0% 邊際改善
        - cooldown chain shift（lesson #19 副作用）：原 2020-09-17 SL 被
          過濾後，2020-09-21 訊號活化並達標 +8.00%（chain shift 為正向）
        - 但仍保留 7 SLs：2019-04-30、2020-01-21、2021-02-19、2022-08-23、
          2023-03-29、2023-07-25，這些 SLs **2DD 維度淺**（僅 2DD < -2%
          的訊號被過濾）
        - 根因：TSM Part A SLs 在 2DD 維度與 winners 高度重疊，2DD cap
          選擇力有限；殘餘 SLs 多為「短暫 regime shock 後的快速反轉」，
          需 multi-day cap 或 oscillator depth 才能區分

================================================================================
跨資產 / 跨策略貢獻（Cross-Asset / Cross-Strategy Findings）
================================================================================
1. **lesson #21 失敗家族擴展至 TSM**（半導體個股 cross-asset 失敗）：
   先前 lesson #21 適用範圍為「single-pure-uptrend 大型廣基 ETF（VOO）」
   或「single-regime growth 個股配 lesson #22 regime gate（NVDA-013）」。
   TSM-010 證明即使是同類半導體個股，**multi-regime 結構差異**（中國
   地緣政治 + 產業週期）使 lesson #22 regime gate **無法跨資產移植**。

2. **lesson #22 cross-strategy 跨資產精煉**：
   - NVDA-013 ★（同 lesson #22 + MBPC framework）：min 0.55
   - **TSM-010 ✗（同框架直接移植）**：min 0.08
   - 跨半導體個股 NVDA→TSM 失敗 **+47% 退化**，反映：
     (a) NVDA 主驅動為 AI 資料中心 secular bull（2024-2025 純 trend）
     (b) TSM 主驅動為 cyclical wafer foundry 景氣（受地緣政治 +
         半導體週期 + 客戶集中度影響，多 regime overlap）
   - **新規則候選**：lesson #22 + MBPC 適用於「single-secular-driver
     高波動個股」，**不適用於多重結構性驅動因子的個股**

3. **進場敏感度方向取決於資產 regime 結構**（lesson #4 邊界擴展）：
   - VOO（單一 secular uptrend）：tight entry 捕捉高品質訊號
   - TSM（multi-regime cyclical）：tight entry 捕捉低品質短期動能
   - 進場敏感度測試需先評估資產 regime 純度

4. **lesson #19 family 邊界擴展（2DD cap on MBPC）**：
   - DIA-012 / CIBR-012 / USO-023（MR 框架）：2DD cap 有效
   - **TSM-010 Att3（MBPC 框架）**：2DD cap 邊際改善（0.03→0.08），
     但仍遠不及 baseline，因 MBPC 進場本質為「shallow pullback after
     breakout」——signal day 2DD 通常 > -3%，2DD cap 主要過濾極端訊號
   - **新規則**：2DD cap 在 MBPC 框架選擇力 << MR 框架，因 MR 進場
     本質為「深 pullback」訊號 day 2DD 廣分布；MBPC 訊號 day 2DD
     集中於淺帶（-3%~0%）

5. **TSM 全 9 次實驗 Sharpe 上限結構性驗證**：TSM-008 RS framework 0.79
   為當前最佳，TSM-010（lesson #22 MBPC）三次迭代全部退化於 0.46
   （TSM-006 momentum pullback baseline）以下，反映 TSM 的最佳訊號
   來源為「TSM/SMH RS spread」（產業內相對強度）而非「絕對動量
   continuation」。RS framework 的 cross-sectional 機制天然消化了
   semi 產業週期 effect，是 TSM cyclical multi-regime 結構下的最佳
   策略類型。

================================================================================
未來方向（Future Directions）
================================================================================
- TSM 全域最優突破 0.79 可能需要：
  (a) 更精細的 RS 框架（動態 SMH 權重、加入 INTC/AMD/QCOM 三角 RS）
  (b) Calendar effect filter（Q4 holiday demand、Q2 capex slowdown）
  (c) 客戶集中度 regime（Apple/NVDA 訂單變動）
  (d) 不應再嘗試純技術面 MBPC / MR 框架——TSM-010 確認 cyclical
      multi-regime 結構性限制
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSM010Config(ExperimentConfig):
    """TSM-010 Multi-Week Regime-Aware MBPC 參數"""

    # === MBPC 基礎 ===
    # Att1：NVDA-013 Att3 直接移植（recency=10、pullback [-3%, -8%]、RSI [40,65]）
    # Att2：VOO-004 Att3 方向（recency=5、pullback [-2%, -5%] 收緊，FAILED）
    # Att3 ★：恢復 NVDA-013 預設 + 啟用 2DD cap secondary filter（FAILED but
    #         marginally less bad than Att1）
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

    # === 多週期趨勢 regime 過濾（lesson #22）===
    # SMA(20) ≥ sma_regime_ratio_min × SMA(60)
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 多週期波動 regime 過濾 ===
    # NVDA-013 Att3 ablation 確認 vol regime 在 MBPC 框架非冗餘
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = True

    # === 2DD cap secondary filter（lesson #19）===
    # 過濾 signal day 2 日報酬過深的訊號。Att3 啟用：threshold=-0.02
    # 結論：在 MBPC 框架選擇力有限（vs MR 框架 DIA-012/CIBR-012 顯著有效）
    use_dd2_cap: bool = True
    dd2_cap_threshold: float = -0.02


def create_default_config() -> TSM010Config:
    """建立預設配置（Att3：NVDA-013 預設 + 2DD cap -2%，三次最佳）"""
    return TSM010Config(
        name="tsm_010_regime_mbpc",
        experiment_id="TSM-010",
        display_name="TSM Multi-Week Regime-Aware Momentum Breakout Pullback Continuation",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
