"""
CIBR-015: Momentum Breakout Pullback Continuation (MBPC)

動機（Motivation）：
    CIBR 14 次實驗 (CIBR-001 ~ CIBR-014) 全部聚焦於均值回歸方向（pullback+WR、
    BB 下軌、RSI(2)、Range Expansion、Higher-Low、Multi-Period Capitulation 等）。
    CIBR-014 Att2 為當前全域最優：min(A,B)† Part B Sharpe **4.08**
    （BB 下軌 + 回檔上限 + 1d cap + ATR ratio BAND）。
    repo 在 CIBR 上**從未探索過趨勢跟蹤 / 動量連續方向**。

    本實驗探索 lesson #21 的跨資產假設：
    "MBPC 在單一結構性上升趨勢資產（VOO 已驗證成功）有效；在週期性 / 事件
     驅動 / 多 regime 資產（FXI、URA、TLT、INDA、EEM、NVDA、FCX、IWM）
     結構性失敗"

    **CIBR 為 sector ETF**（網路安全板塊），既非 broad-uptrend ETF（如 VOO），
    亦非個股或政策驅動 EM。CIBR 在 2024-2025 牛市期間有清晰上升趨勢，但
    2022 科技熊市產生顯著回撤——介於 VOO（純結構性上升）與 FXI（多 regime
    重疊）之間。本實驗為 lesson #21 邊界擴展試驗：MBPC 是否能延伸至
    **sector ETF（具明顯 regime 切換）**？

    **與 VOO-004 Att3 的關鍵差異**（lesson #7 vol scaling）：
    - CIBR 日波動 1.53% vs VOO ~1.0%（1.53x）
    - Pullback 範圍按 vol 縮放：[-2%, -3%] → [-3%, -4.5%]
    - TP/SL 按 vol 縮放：+3.0%/-2.5% → +4.0%/-3.5%
    - 持倉 / 冷卻維持（時間維度不縮放）

策略方向：趨勢跟蹤 / 動量連續（Trend-following / Momentum Continuation）
    捕捉 CIBR 強趨勢中的「Donchian 新高 → 淺回檔 → 多頭 K 棒確認」連續模式。

進場條件（Entry conditions）：
    1. 近 N 日內曾創 Donchian 20 日新高（breakout freshness）
    2. Close > SMA(50)（中期趨勢向上）
    3. 當前 Close 相對於 5 日高點回檔在 [pullback_max, pullback_min] 範圍
       （vol-scaled 淺回檔 -3% ~ -4.5%）
    4. RSI(14) ∈ [rsi_min, rsi_max]（非深度超賣，亦非過熱）
    5. Close > Open（當日多頭 K 棒確認）
    6. （Att2/Att3）SMA(20) regime gate（buffered or BOX，lesson #22 cross-strategy 移植）
    7. 冷卻 10 個交易日

出場條件（Exit conditions）：
    - TP +4.0%（VOO-004 Att3 +3.0% 按 1.53x vol scale）
    - SL -3.5%（VOO-004 Att3 -2.5% 按 1.4x vol scale）
    - 最長持倉 20 天
    - 滑價 0.10%（CIBR 流動性中等，與 VOO 標準同）
    - 悲觀認定：是

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價

迭代歷程（Iteration Log）：

Att1（Baseline，VOO-004 Att3 直接 vol-scaled 移植）
    進場：breakout_recency=5, Close>SMA(50), pullback [-3%,-4.5%], RSI [40,60],
         Close>Open, cd 10
    出場：TP+4.0%/SL-3.5%/20 天
    結果：
        Part A: 10 訊號, WR 50.0%, 累計 +1.29%, Sharpe **0.05**
        Part B:  3 訊號, WR 33.3%, 累計 -0.35%, Sharpe **-0.02**
        min(A,B): **-0.02**（遠低於 CIBR-014 Att2† 的 4.08，也低於前任 CIBR-012 Att3 的 0.49）
    Part A 失敗分析：
        - 5 筆 SL: 2020-01-28（COVID 前夕 17 天 SL）/ 2021-02-18（科技股輪動 2 天 SL）
          / 2022-03-09（升息 2 天 SL）/ 2022-04-07（4 月熊市 8 天 SL）/
          2023-08-03（Fitch 美債降評 9 天 SL）
        - SLs 集中於 macro / regime-shift 日（與 NVDA-009 Att1 相同模式，
          但訊號密度 2.0/yr 較低）
        - WR 50.0% 顯示 MBPC 在 CIBR 多 regime 結構下偽訊號率高
    Part B 失敗分析：
        - 訊號密度 1.5/yr（過低，僅 3 訊號 5 SD 統計可信度不足）
        - 2025-07-14 SL: CIBR 牛市中淺回檔不反彈
        - 2025-10-14 expiry: 進場後 20 天橫盤 -0.60%

Att2（Buffered SMA(20) >= 0.99 × SMA(60) regime gate，lesson #22 cross-strategy 移植）
    調整：require_sma_regime=True, k_min=0.99, BOX 關閉
    結果：
        Part A:  9 訊號, WR 55.6%, 累計 +5.07%, Sharpe **0.16**（+220% vs Att1）
        Part B:  3 訊號（不變）, Sharpe **-0.02**（不變）
        min(A,B): **-0.02**（仍失敗）
    分析：
        - Part A 改善：buffered SMA gate 過濾 2022-03-09 SL（升息初期 SMA20/60<0.99）
        - Part B 完全非綁定：3 訊號的 SMA20/60 ratio 皆已 >= 0.99
        - Part B 兩筆 losers (2025-07-14 SL / 2025-10-14 expiry) regime 正常，
          失敗原因不在 regime 層級而是 sector-specific 微觀結構

Att3（Regime BOX [k_min=1.00, k_max=1.09]，COPX-011 路徑）
    調整：require_sma_regime_box=True, k_min=1.00 嚴格, k_max=1.09 過熱上限
    結果：
        Part A:  8 訊號, WR 50.0%, 累計 +1.03%, Sharpe **0.05**（退回 Att1 水準）
        Part B:  3 訊號（不變）, Sharpe **-0.02**（不變）
        min(A,B): **-0.02**（失敗）
    分析：
        - k_min=1.00 嚴格反而過濾 2021-01-27 winner（SMA20/60 在 0.99-1.00 區間）
        - k_max=1.09 對 2025-07-14 SL 非綁定（該訊號 ratio 已在 [1.00, 1.09] 內）
        - 訊號數 9→8 但 wins 5→4，filter 移除贏家而非輸家
        - **拒絕 lesson #22 v2 假設於 CIBR**：COPX-011 regime BOX 結構性發現
          在 CIBR sector ETF 上不重現

**三次迭代結論（CIBR-015 全部失敗，CIBR-014 Att2 仍為全域最優）**：

1. **MBPC 結構在 CIBR 上失敗**（repo 第 4 次 MBPC 試驗）
   驗證並擴展 cross_asset_lesson #21 邊界：sector ETF（具明顯 regime 切換的板塊
   集中型 ETF）加入 MBPC 失敗清單
   - 既有失敗：FXI-012（政策驅動 EM）、NVDA-009（多 regime 個股）、IWM-014（小型股寬基）
   - 新增失敗：CIBR-015（網路安全 sector ETF）
   - 唯一成功：VOO-004 Att3（純結構性上升 broad ETF）
   **新規則**：MBPC 不適用於「具顯著 regime 切換的 sector ETF」，原因為 sector
   集中度使 macro shock / sector-rotation 直接打擊單一 sector，false breakout
   率高於 broad ETF

2. **lesson #22 cross-strategy 移植在 sector ETF MBPC 上失效**
   - NVDA-013（個股 MBPC + buffered SMA regime）成功，min(A,B) 0.41→0.55
   - CIBR-015 Att2（sector ETF MBPC + buffered SMA 0.99）：Part A 改善但
     Part B 完全非綁定 → 結構性失敗
   **規則更新**：lesson #22 buffered SMA regime gate 在 MBPC 框架下
   - 個股（NVDA）：成功（macro + sector 雙重 regime 風險可被 SMA 抓到）
   - sector ETF（CIBR）：失敗（sector-specific microstructure 不在 SMA 維度）

3. **lesson #22 v2「regime BOX」在 sector ETF MBPC 上失效**
   COPX-011 商品/礦業 ETF 發現 BOX 結構（k_min + k_max 雙向）成功，但 CIBR
   sector ETF 不重現該模式——COPX 為商品週期性 ETF，CIBR 為事件/技術週期性
   ETF，winners/losers 在 SMA ratio 維度的分佈結構不同

4. **Part B 訊號稀缺結構性問題**
   3 次迭代 Part B 均維持 3 訊號（1.5/yr），統計可信度不足。MBPC 訊號生成
   結構在 CIBR 1.53% vol sector ETF 上自然稀疏，無法經由放寬 entry 改善
   （放寬將反向引入更多 Part A SLs）

**CIBR 失敗策略類型達 9 種**（前 8 種：BB Squeeze、RSI(2)、RS momentum、
Key Reversal Day、NR7、Range Expansion、Higher-Low Confirmation、20日回看；
新增 9：Momentum Breakout Pullback Continuation）。CIBR-014 Att2
（Multi-Period Capitulation-Strength Filter MR + ATR-Vol Ceiling）仍為全域最優
（min(A,B)† Part B Sharpe 4.08）。

最終參數（Att3，僅作為失敗實驗的記錄參考）：
    donchian_period: 20
    breakout_recency_days: 5
    pullback_lookback: 5
    pullback_min: -3%
    pullback_max: -4.5%
    sma_trend_period: 50
    rsi_min / rsi_max: [40, 60]
    bullish_close_required: True
    require_sma_regime: True
    sma_regime_short: 20
    sma_regime_long: 60
    sma_regime_k_min: 1.00（strict）
    require_sma_regime_box: True
    sma_regime_k_max: 1.09
    cooldown_days: 10
    出場：TP +4.0% / SL -3.5% / 20 天，滑價 0.10%，悲觀認定 True
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR015Config(ExperimentConfig):
    """CIBR-015 Momentum Breakout Pullback Continuation 參數"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 5  # 近 5 日曾創 20 日新高

    # Shallow pullback range (vol-scaled from VOO-004 Att3 [-2%, -3%])
    pullback_lookback: int = 5
    pullback_min: float = -0.03  # -3% 淺回檔下限（vol-scaled, CIBR 1.53% / VOO 1.0%）
    pullback_max: float = -0.045  # -4.5% 淺回檔上限

    # Trend filter
    sma_trend_period: int = 50

    # RSI neutrality filter
    rsi_period: int = 14
    rsi_min: float = 40.0
    rsi_max: float = 60.0

    # Bullish close confirmation
    bullish_close_required: bool = True

    # Multi-week SMA regime gate (Att2/Att3, lesson #22 cross-strategy 移植)
    # Att3：Regime BOX [k_min=1.00, k_max=1.09]（COPX-011 路徑）
    # 同時過濾 (a) bear-market 假突破 (b) late-bull 過熱訊號
    require_sma_regime: bool = True
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_k_min: float = 1.00  # SMA(20) >= k_min × SMA(60)
    require_sma_regime_box: bool = True
    sma_regime_k_max: float = 1.09  # SMA(20) <= k_max × SMA(60)

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> CIBR015Config:
    return CIBR015Config(
        name="cibr_015_momentum_pullback",
        experiment_id="CIBR-015",
        display_name="CIBR Momentum Breakout Pullback Continuation",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.040,  # +4.0% (vol-scaled from VOO +3%)
        stop_loss=-0.035,  # -3.5% (vol-scaled from VOO -2.5%)
        holding_days=20,
    )
