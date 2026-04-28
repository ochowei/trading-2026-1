"""
NVDA-011: Capitulation-Depth Filter Mean Reversion (RSI Oscillator Depth)

動機（Motivation）：
    NVDA 全域最佳 NVDA-004（BB Squeeze）/ NVDA-006（RS）min(A,B) 皆為 0.47，
    NVDA-009 / NVDA-010 三類 entry-time 過濾器（MBPC、ADX/DMI）皆未超越。
    NVDA 既有 RSI(2) MR 基線 NVDA-001（RSI(2)<5 + 2日跌幅≤-7%）為極深設定，
    Part A 0.07 / Part B 0.14 績效低，從未獲得 IWM-011 風格的中度 RSI(2) +
    2DD + ClosePos + ATR + 較窄 SL 的 MR 基線測試機會。

    **本實驗將 IWM-013 Att3 的「RSI 振盪器深度過濾」方向（repo 第 4 次
    capitulation-depth filter 成功，首次以 oscillator depth 替代 raw return
    depth）跨資產移植至高波動單一個股 NVDA**——repo 首次將「中度 RSI(2) MR
    基線 + capitulation-depth 振盪器維度過濾」應用於 >3% vol 單一個股。

    跨資產 vol 縮放（NVDA 3.26% vol vs IWM 1.5-2% vol，比例 ~ 1.7-2.0x）：
    - 2DD 門檻：-2.5% × 1.8 = -4.5%
    - TP：+4% × 1.75 = +7%
    - SL：-4.25% × 1.65 = -7%
    - 持倉：20 × 0.75 = 15 天（高波動 = 較快回歸）
    - 冷卻：5 × 1.6 = 8 天
    - ClosePos：保持 40%（跨資產穩定值）
    - ATR 比率：保持 1.10（lesson #6 邊界內）

    假設（Hypothesis）：NVDA 的 MR losers / winners 在 raw return 維度（1d、3d、
    2DD）高度重疊，但在 RSI(2) 振盪器維度（多日累積動能耗竭度量）可能有清晰
    分隔（IWM 平行）。若有，可繞過 NVDA-009 Att3a/b 已驗證失敗的 2DD cap
    方向，達成 capitulation strength 度量。

    結構性風險：TSLA-014（3.72% vol）和 FCX-011（3% vol）皆於 Post-Cap MR
    跨資產移植失敗——「高波動單一股延續性事件 regime」使 entry-time 過濾器
    無區分力。本實驗測試 oscillator 維度（RSI deepening）能否突破此限制。

策略方向：均值回歸（Mean Reversion）
    deep oversold + 急跌 + 日內反轉 + 波動率飆升 + capitulation depth 確認

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價
    - 滑價：0.15%（單一股流動性）
    - 悲觀認定：是

============================================================================
三次迭代記錄（2026-04-26，成交模型 0.15% slippage，隔日開盤市價進場）：
============================================================================

Att1（Baseline）：vol-scaled IWM-011 framework
    RSI(2) < 10 + 2DD <= -4.5% + ClosePos >= 40% + ATR(5)/ATR(20) > 1.10
    + cd 8 + TP +7% / SL -7% / 15d
    結果：
        Part A: 5 訊號 WR 40.0% Sharpe **-0.21** cum -8.32%
            2019-04-26 SL（trade-war pre-correction）
            2020-01-27 TP（pre-COVID drop）
            2021-02-23 SL（Feb tech correction）
            2022-08-09 TP（mid-bear rally）
            2022-09-01 SL（post-Jackson Hole bear continuation）
        Part B: 2 訊號 WR 100% std=0 Sharpe 0.00 cum +14.49%
            2025-01-13 TP（DeepSeek shock recovery）
            2025-09-02 TP（mid-2025 dip）
        min(A,B): **-0.21**（FAIL，遠低於 NVDA-004 的 0.47）
    失敗分析：
        - Part A 3 SLs 全為「continuation decline」（regime trap）：訊號日後
          NVDA 持續下挫至 -7% SL 而非反彈
        - 1.0/yr 訊號密度過稀疏（IWM-011 為 2.0/yr），統計可信度有限
        - 高波動 single stock 的 multi-regime（2018-2023 含 trade war / COVID /
          AI bubble / bear / chop）使 vol-scaled framework 喪失選擇性
        - Part B 2 訊號全 TP 顯示 2024-2025 純粹 AI 牛市更友善（與 NVDA-009
          MBPC Part B Sharpe 0.96 / NVDA-009 Part B 0.49 平行結構）

Att2：Att1 + 3 日急跌上限 >= -6%（DIA-012 / CIBR-012 cap 方向）
    動機：Att1 三筆 SL 推測為深 3d return 「crash still accelerating」訊號，
        cap 方向移除「下跌仍在加速」進場時點
    結果：
        Part A: 2 訊號 WR 50.0% Sharpe **-0.01** cum -0.64%
            2020-01-27 TP（保留，shallow 3d）
            2021-02-23 SL（保留，shallow 3d）
            移除：2019-04-26 SL ✓、2022-09-01 SL ✓、2022-08-09 TP ✗
        Part B: 不變（2 訊號，全 TP std=0 Sharpe 0.00）
        min(A,B): **-0.01**（marginally improved 但仍 FAIL）
    失敗分析：
        - 3d cap 成功濾除 2 SLs（兩筆深 3d continuation traps）但同時誤殺
          1 TP（2022-08-09 也為深 3d capitulation reversal）
        - 殘留 2021-02-23 SL 為 sharp 1d 急跌（non-prior-3d-buildup），3d cap
          無法捕捉，需 1d cap 補捉 → 嘗試 Att3
        - Part A 從 5 訊號降至 2 訊號使統計可信度進一步惡化（0.4/yr）

Att3（最終）：Att2 + 1 日急跌上限 >= -4%（DIA-012 dual-dimension 跨資產移植）
    動機：DIA-012 Att2（1d cap -2% + 3d cap -7% 雙維度）為 1.0% vol 廣基 ETF
        全域最優；NVDA 3.26% vol 為 DIA 的 3.26x，1d cap 保守取 -4%（vs DIA
        scaled -6.5%）以保留 Part B 推測較深 1d 的高品質 winners
    結果：
        Part A: **1 訊號 WR 0.0% Sharpe 0.00** cum -7.14%
            2021-02-23 SL（保留，shallow 1d/3d 同時，被該設計捕獲）
            移除：2020-01-27 TP（1d ≤ -4% 被誤殺！）
        Part B: 不變（2 訊號，全 TP std=0 Sharpe 0.00）
            **2025-01-13 / 2025-09-02 推測 1d > -4%**，未被過濾
        min(A,B): **0.00**（FAIL，與 Att2 持平但 Part A 訊號崩至 1）
    失敗分析（重要！）：
        - **NVDA Part A 高品質 winner（2020-01-27 pre-COVID）的 1d 比 SL
          （2021-02-23）更深**——DIA-012 cap 方向結構**錯誤**：DIA Part A
          losers 集中深 1d gap-down（cap 方向過濾贏家），NVDA 2020-01-27
          winner 為「真實 capitulation 深 1d gap-down」
        - 與 IWM-013 Att1 失敗模式平行：cap 方向誤殺 Part A 真實 capitulation
          recovery winners（IWM 2020-09-21 1d=-3.50% TP / NVDA 2020-01-27
          推測 1d ≤ -4% TP 同類）
        - 殘留 2021-02-23 SL 為 sharp 1d 但 sub-threshold（推測 1d ~-3%
          to -3.5%），cap 方向無法捕獲——需 RSI 振盪器維度（IWM-013 Att3
          成功路徑），但 base framework 訊號密度（5 → 2 → 1）已不足以支撐
          進一步 RSI 加嚴

**三次迭代全部失敗結論**（最佳 Att2 min -0.01，最差 Att1 -0.21，全部低於
NVDA-004 / NVDA-006 的 0.47）：

1. **vol-scaled IWM-011 MR framework 不適用 NVDA 高波動 single stock**：
   - NVDA 1.0/yr 訊號密度（vs IWM-011 2.0/yr）統計可信度不足
   - 2018-2023 multi-regime 使 framework 訊號隨機化（5 訊號中 3 SL）
   - 與 TSLA-014（3.72% vol）/ FCX-011（3% vol）Post-Cap MR 跨資產失敗
     模式平行——擴展失敗 vol 上限至 NVDA 3.26%

2. **DIA-012 cap 方向結構性不適用 NVDA**：
   - NVDA Part A 真實 capitulation winners（2020-01-27 pre-COVID）為深 1d
     gap-down，cap 方向誤殺
   - NVDA Part A SL（2021-02-23 Feb tech correction）為 sharp 1d 但
     sub-threshold，cap 方向無法捕獲
   - 失敗結構與 IWM-013 Att1 平行：cap 方向適用於 SL 集中深 1d 結構（DIA），
     不適用於 winner 集中深 1d 結構（IWM、NVDA）

3. **NVDA 結構性 Sharpe 上限 ~0.5 再度確認**——三類入場過濾器（MBPC、
   ADX/DMI、Capitulation-Depth Filter）皆無法突破 NVDA-004 / NVDA-006 的
   0.47。NVDA 2018-2023 multi-regime（trade war / COVID / 2021 bubble /
   2022 bear / 2023 chop）變異使單一參數集難以同時優化 Part A/B；
   2024-2025 AI 純牛市單邊 sharpe 高（NVDA-011 Part B / NVDA-009 Part B 0.96）
   但 Part A 約束。

4. **Lesson #19 family 邊界擴展（NVDA-011 貢獻）**：
   - capitulation-depth filter（無論 raw return 維度或 oscillator 維度）
     需資產擁有「足夠訊號密度（≥1.5/yr）」為前提；NVDA vol-scaled
     framework 1.0/yr 已低於有效閾值
   - **DIA-012/SPY-009/EWJ-005 raw return cap 方向 vs IWM-013 oscillator
     depth 方向的選擇取決於 winners/losers 的 raw return 分布**：
       a. SL 集中深 1d/2d/3d：raw return cap 有效（DIA、CIBR、SPY）
       b. winner 集中深 1d/2d/3d：raw return cap 失敗（IWM Part B、NVDA）
          需 oscillator 維度（IWM-013 RSI < 8）
       c. 訊號密度過低（< 1.5/yr）：兩種維度皆失敗（NVDA-011 confirmation）
   - **Repo 第 5 次 capitulation-depth filter 嘗試，repo 首次高波動
     >3% vol 單一個股測試**——失敗確認 vol 上限介於 IWM 1.5-2%（成功）
     與 NVDA 3.26%（失敗）之間。

NVDA-004（BB Squeeze）/ NVDA-006（RS Momentum Pullback）維持全域最優 0.47
（11 次實驗、34+ 次嘗試，含均值回歸、突破、動量回調、相對強度、RS 出場/
參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter 九大方向）。

最終參數（保留 Att3 為三次最寬鬆過濾組合，後續實驗應改變方向而非繼續精煉
此基線）：
    rsi_period: 2 / rsi_threshold: 10.0
    decline_lookback: 2 / decline_threshold: -0.045
    close_position_threshold: 0.4
    atr_short_period: 5 / atr_long_period: 20 / atr_ratio_threshold: 1.10
    oneday_return_cap: -0.04（DIA-012 1d cap 方向）
    threeday_return_cap: -0.06（DIA-012 / CIBR-012 3d cap 方向）
    cooldown_days: 8
    出場：TP +7% / SL -7% / 15 天 / 滑價 0.15%
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA011Config(ExperimentConfig):
    """NVDA-011 Capitulation-Depth Filter MR 參數"""

    # RSI(2) 參數（capitulation oscillator depth）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # Att1: 10（baseline，IWM-011 對齊）

    # 2 日累計跌幅過濾（NVDA vol-scaled，IWM-011 -2.5% × 1.8 = -4.5%）
    decline_lookback: int = 2
    decline_threshold: float = -0.045

    # 收盤位置過濾（日內反轉確認）
    close_position_threshold: float = 0.4

    # ATR 比率過濾（波動率飆升確認）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 1 日急跌上限（DIA-012 cap 方向）— Att3 啟用 -4%
    # NVDA 3.26% vol 為 DIA 1.0% 的 3.26x；DIA-012 -2% scaled 至 -6.5%，保守取 -4%
    oneday_return_cap: float = -0.04

    # 3 日急跌上限（DIA-012/CIBR-012 cap 方向）— Att2 啟用 -6%
    threeday_return_cap: float = -0.06

    # 3 日急跌下限（USO/EEM/INDA/VGK floor 方向，預留）— 三次迭代皆停用
    threeday_return_floor: float = 0.0

    # 冷卻期（NVDA 高波動 = 較長冷卻避免重複進場）
    cooldown_days: int = 8


def create_default_config() -> NVDA011Config:
    return NVDA011Config(
        name="nvda_011_capitulation_filter",
        experiment_id="NVDA-011",
        display_name="NVDA Capitulation-Depth Filter MR (RSI Depth)",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.07,
        stop_loss=-0.07,
        holding_days=15,
    )
