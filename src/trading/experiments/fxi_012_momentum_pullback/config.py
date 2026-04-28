"""
FXI-012: Momentum Breakout Pullback Continuation (MBPC)

動機（Motivation）：
    FXI-005 Att3 為 FXI 目前全域最優（min(A,B) 0.38），但存在嚴重的 Part A/B
    不平衡問題：
        Part A (2019-2023): 26 訊號, WR 65.4%, 累計 +55.00%, Sharpe 0.38
        Part B (2024-2025):  5 訊號, WR 80.0%, 累計 +20.59%, Sharpe 1.61

    累計報酬差距 34.4 pp（比例 2.67:1 = 163%，遠超 30% 目標）；訊號數比例
    5.2:1（Part A 5.2/yr vs Part B 2.5/yr，遠超 50% 目標）。核心不平衡根因：
    Part A 中國長期熊市（2022 政策衝擊、2019-2020 貿易戰）產生大量 pullback+WR
    均值回歸訊號；Part B 2024-2025 中國刺激政策驅動 V-shape 反彈，深回檔
    訊號稀疏，但 MR 未能捕捉到上升趨勢中的連續性機會。

    **本實驗探索 repo 中較少使用的「趨勢跟蹤 + 動量」方向**（已探索：MR、突破、
    配對交易；較少：動量連續、純趨勢跟蹤）。FXI 尚未嘗試過純「絕對動量」策略：
    - FXI-007 為 RS 動量（vs EEM），失敗（單一國家 EM RS 由政策驅動，非結構性）
    - FXI-003 為 BB Squeeze 突破，失敗（政策驅動下突破後快速反轉）
    - **FXI-012 為 repo 首次於 FXI 試驗「Donchian 新高 + 淺回檔連續進場」
      絕對動量模式**

策略方向：趨勢跟蹤 / 動量連續（Trend-following / Momentum Continuation）
    Strategy direction: Momentum pullback continuation with Donchian breakout
    freshness filter, targeting FXI's stimulus-driven V-shape rallies

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價
    - 滑價：0.15%（FXI 為流動性較低的單一國家 EM ETF）
    - 悲觀認定：是

迭代歷程（Iteration Log）：

Att1（Baseline）—— Donchian 新高 + 淺回檔連續進場
    進場：
        1. 近 5 日內曾創 20 日新高（Donchian breakout freshness）
        2. Close > SMA(50)
        3. 5 日高點回檔 2-5%（淺回檔）
        4. RSI(14) ∈ [40, 60]（中性）
        5. 冷卻 10 天
    出場：TP +4.0% / SL -3.5% / 15 天
    結果：
        Part A: 26 訊號, WR 42.3%, 累計 -9.96%, Sharpe -0.09
        Part B: 12 訊號, WR 58.3%, 累計 +9.42%, Sharpe 0.24
        min(A,B): -0.09（遠低於 FXI-005 的 0.38）
    失敗分析：
        - Part A 2019-2023 中國熊市期產生大量假 Donchian 突破
        - SMA(50) 單一趨勢過濾太寬鬆——熊市反彈中常被觸及
        - Part B WR 58.3% 顯示策略在真正上升趨勢中有部分效用

Att2（基於 Att1）—— 收緊趨勢 regime 過濾
    調整：
        - 新增 SMA(20) > SMA(50)（短中均線黃金排列，確認短期動能）
        - RSI 範圍收緊 [45, 58]
    結果：
        Part A: 16 訊號, WR 43.8%, 累計 -7.11%, Sharpe -0.11
        Part B: 10 訊號, WR 70.0%, 累計 +17.84%, Sharpe **0.55**（+129% vs Att1）
        min(A,B): -0.11（Part A 仍失敗）
    分析：
        - Part B 大幅改善（Sharpe 0.24→0.55），超越 FXI-005 Part A Sharpe 0.38
        - Part A 惡化（-0.09→-0.11）：SMA(20)>SMA(50) 黃金排列**無法濾除**
          2019 貿易戰 / 2021 監管 / 2023 弱勢期的假突破
        - 訊號數 26→16（-38%）但 WR 僅 42.3%→43.8%（非選擇性過濾）
    **核心發現**：單純黃金排列不足以代表「真上升 regime」；需要 SMA 本身
        持續上升（趨勢 slope 為正）

Att3（基於 Att1/Att2）—— 新增 SMA(50) slope 上升條件（真 bull regime 過濾）
    調整：
        - 新增 SMA(50)[今日] > SMA(50)[60 日前]（SMA50 本身持續上升 60 日）
        - 保留 Close > SMA(50)，**移除 SMA(20) > SMA(50)**（Att2 驗證無效）
        - 保留 RSI [45, 58]
    結果：
        Part A:  8 訊號, WR 37.5%, 累計 -6.55%, Sharpe **-0.21**（惡化）
        Part B:  9 訊號, WR 55.6%, 累計 +7.86%, Sharpe 0.26（從 Att2 的 0.55
                 降至 0.26）
        Part C:  1 訊號, WR 100%, 累計 +4.00%, Sharpe 0.00
        min(A,B): **-0.21**（三次迭代中最差）
    失敗分析：
        - SMA slope filter **雙向惡化**：Part A 47.3% 訊號減少（16→8）但 WR
          下滑（43.8%→37.5%）；Part B WR 70%→55.6% 且 Sharpe 減半（0.55→0.26）
        - **關鍵反直覺發現**：FXI 最佳動量連續訊號常發生在「SMA(50) 仍在
          下降但即將轉折」的 regime 轉換期（如 2022 Q4 reopening 初期、
          2024 Q3 刺激政策初期）；SMA slope 已轉正時往往已錯過最佳進場點
        - Att3 同時**移除 Part B 優勢**（WR 從 70% 崩至 55.6%）——slope filter
          在 2024-2025 刺激期也出現「滯後觸發」問題

**三次迭代全部失敗結論**（min 最佳 Att1 的 -0.09，仍遠低於 FXI-005 的 0.38）：

    FXI-012 為 repo 首次於 FXI 試驗「絕對動量連續」（非 RS 動量）策略，
    三次迭代均失敗揭示：

    1. **動量連續在政策驅動單一國家 EM ETF 結構性失效**：
       - Att1（基線）：Part A 熊市假突破率過高（WR 42.3%）
       - Att2（黃金排列過濾）：雙均線排列無法區分熊市反彈
       - Att3（SMA slope 過濾）：已轉正 slope 反而為滯後信號
       - 核心：中國政策衝擊（貿易戰、監管、疫情）常於 regime 轉換期出現，
         所有趨勢過濾器在此時點皆為**滯後指標**，Donchian + SMA 框架
         同時受到假突破與滯後觸發兩面傷害

    2. **擴展 lesson #25 與 lesson #52 邊界**：
       - lesson #25 已記錄 RS 動量（相對強度）在政策驅動單一國家 EM 失敗
       - **本實驗新增**：絕對動量連續（Donchian 新高 + 淺回檔）同樣失敗
       - lesson #52 已記錄所有短週期反轉結構（BB 下軌、BB Squeeze、Stoch、
         Failed Breakdown、Gap-Down Capitulation）在 FXI 失敗
       - **本實驗新增**：趨勢延續結構（動量連續）亦失敗——FXI 兼具「短週期
         反轉失效」與「趨勢延續失效」雙重結構性限制

    3. **Part A/B 不平衡根因為 FXI 內生結構**：
       - MR 框架（FXI-005）Part A 訊號多 / Part B 訊號少
       - 動量框架（FXI-012）Part A 假訊號多 / Part B 稀疏但品質相對較好
       - 兩種相反方向的策略都無法平衡 A/B ——表明 FXI 的結構性風險
         （政策週期、美中關係、匯率）在不同時期產生**完全不同類型**的
         市場行為，任何單一技術分析框架皆難以跨越

    4. **FXI-005 Att3 維持全域最優**（12 次實驗、36+ 次嘗試），已證明
       pullback+WR+ClosePos+ATR 混合過濾為 FXI 政策驅動環境下最佳結構。
       Part A/B 不平衡為 FXI 固有結構問題，非策略可完全解決。

    5. **跨資產啟示（待驗證）**：動量連續策略在非政策驅動的單一國家 ETF
       （如 EWT 半導體驅動、EWZ 商品驅動）可能有效，需於後續實驗驗證。
       對於政策驅動單一 EM 國家 ETF（FXI、INDA 政策面），動量連續應
       列為禁忌方向。

最終參數（Att3）：
    pullback_lookback: 5 日
    pullback_min: -0.02（2% 淺回檔下限）
    pullback_max: -0.05（5% 淺回檔上限）
    donchian_period: 20 日
    breakout_recency_days: 5
    sma_trend_period: 50
    sma_slope_lookback: 60（Att3 新增：SMA50 slope 回看）
    require_sma20_above_sma50: False（Att3 移除：Att2 驗證無效）
    require_sma_slope_positive: True（Att3 啟用）
    rsi_period: 14
    rsi_min: 45
    rsi_max: 58
    cooldown_days: 10
    出場：TP +4.0% / SL -3.5% / 15 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI012Config(ExperimentConfig):
    """FXI-012 Momentum Breakout Pullback Continuation 參數（Att3 最終）"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 5

    # Shallow pullback range
    pullback_lookback: int = 5
    pullback_min: float = -0.02  # -2% 淺回檔下限
    pullback_max: float = -0.05  # -5% 淺回檔上限

    # Trend filter (Att3: SMA50 slope 上升 bull regime 過濾)
    sma_short_period: int = 20
    sma_trend_period: int = 50
    sma_slope_lookback: int = 60  # Att3: SMA50 今日 > SMA50 60 日前
    require_sma20_above_sma50: bool = False  # Att3: 移除（Att2 驗證無效）
    require_sma_slope_positive: bool = True  # Att3: 啟用 slope 過濾

    # RSI neutrality filter
    rsi_period: int = 14
    rsi_min: float = 45.0
    rsi_max: float = 58.0

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> FXI012Config:
    return FXI012Config(
        name="fxi_012_momentum_pullback",
        experiment_id="FXI-012",
        display_name="FXI Momentum Breakout Pullback Continuation",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.04,
        stop_loss=-0.035,
        holding_days=15,
    )
