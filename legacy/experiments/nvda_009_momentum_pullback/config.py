"""
NVDA-009: Momentum Breakout Pullback Continuation (MBPC)

動機（Motivation）：
    NVDA 目前全域最優為 NVDA-004 BB Squeeze Breakout（min(A,B) 0.47）與
    NVDA-006 RS Momentum（min(A,B) 0.47 同分）。兩者皆以「突破」為主，
    但尚未測試過「絕對動量延續」——即「Donchian 新高 → 淺回檔 → 續漲」
    此結構性經典動量連續模式。

    **本實驗探索 repo 中較少使用的「趨勢跟蹤 / 動量連續」方向**。
    repo 已飽和的方向：均值回歸（NVDA-001/002）、突破（NVDA-003/004）、
    RS 配對（NVDA-006/007/008）、短期動量回調（NVDA-005）。
    **尚未嘗試**：Donchian 絕對動量 + 淺回檔延續（本實驗）。

    此策略類型僅在 FXI-012 試過（失敗，因 FXI 政策驅動的假突破與滯後觸發），
    但 NVDA 為純動量驅動（AI / 半導體），無政策衝擊週期，應更適合此結構。

策略方向：趨勢跟蹤 / 動量連續（Trend-following / Momentum Continuation）
    捕捉 NVDA 強趨勢中的「回檔→續漲」階梯式動量延續。

進場條件（Entry conditions）：
    1. 近 N 日內曾創 Donchian 20 日新高（breakout freshness）
    2. Close > SMA(50)（中期趨勢向上）
    3. 當前 Close 相對於 5 日高點回檔在 [pullback_max, pullback_min] 範圍
       （淺回檔 3-8% — NVDA 3.26% vol 下 5% ≈ 1.5σ）
    4. RSI(14) ∈ [rsi_min, rsi_max]（非深度超賣，亦非過度超買）
    5. Close > Open（當日多頭 K 棒確認）
    6. 冷卻 10 個交易日

出場條件（Exit conditions，基於 NVDA-004/006 驗證之甜蜜點）：
    - TP +8%（NVDA-003 Att2 驗證 TP+10% 反使贏家變到期/停損）
    - SL -7%（NVDA-003 Att3 驗證 SL-5% 過緊、NVDA-004 Att1 驗證 SL-8% 無救回）
    - 最長持倉 20 天（NVDA 一般於 7-10 天解決）
    - 滑價 0.15%（NVDA 高波動 + 個股）

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價
    - 滑價：0.15%
    - 悲觀認定：是

迭代歷程（Iteration Log）：

Att1（Baseline）—— Donchian 新高 + 淺回檔 + SMA(50) + RSI [40,65]
    進場：
        1. 近 10 日內曾創 20 日 Donchian 新高
        2. Close > SMA(50)
        3. 5 日高點回檔在 [-3%, -8%]
        4. RSI(14) ∈ [40, 65]
        5. Close > Open
        6. 冷卻 10 日
    出場：TP +8% / SL -7% / 20 天
    結果：
        Part A: 34 訊號, WR 67.6%, 累計 +142.32%, Sharpe **0.41**
        Part B:  8 訊號, WR 75.0%, 累計 +47.30%,  Sharpe **0.96**
        min(A,B): **0.41**（低於 NVDA-004 / NVDA-006 的 0.47）
    A/B 平衡：
        訊號比 34/8 = 4.25:1（年化 6.8/yr vs 4.0/yr → 1.7:1 = 41% gap，< 50% ✓）
        累計 A/B 年化：A +28.46%/yr、B +23.65%/yr → 相對差 16.9%（< 30% ✓）
        **A/B 平衡目標達成**，但 Sharpe 目標未達
    Part A 失敗分析：
        - 11 筆 SL 集中於 2020 COVID（1）/ 2021 late-bull（3）/ 2022 bear（2）
          / 2023 summer consolidation（3）/ 其他（2）
        - Part A Sharpe 拖累來自 2021-2023 market regime transition 期間，
          突破後續漲失敗率偏高（AI hype → correction 過度延伸後的 shallow
          pullback 常被後續更深下跌吞噬）
        - Part B 2024-2025 AI 牛市中此類型訊號極佳（WR 75%, Sharpe 0.96）

Att2（Based on Att1）—— 加入 SMA(200) regime 閘門 + 收緊 RSI 上限 60
    調整：
        - 新增 Close > SMA(200)（長期趨勢 regime 過濾）
        - RSI_max：65 → 60（濾除過熱進場）
    結果：
        Part A: 21 訊號, WR 66.7%, 累計 +66.17%,  Sharpe **0.38**（-7% vs Att1）
        Part B:  6 訊號, WR 83.3%, 累計 +46.87%,  Sharpe **2.22**（+131% vs Att1）
        min(A,B): **0.38**（較 Att1 惡化）
    失敗分析：
        - Part A 訊號 34→21（-38%），但 WR 67.6%→66.7% 僅微降 → **非選擇性過濾**
        - 移除 9 筆贏家（23→14）vs 移除 5 筆 SL（11→6）→ 贏家/SL 比 9/5=1.8
          低於整體 23/11=2.1，過濾方向錯誤
        - Part B 大幅改善但 Part A 惡化，A/B 更加分裂
        - 核心問題：SMA(200) 在 2022 熊市初期（NVDA 2022-01~04）
          剛跌破 SMA(200) 的信號被系統性排除，但這些訊號常為 Att1
          的贏家而非 SL（NVDA 2022-07-25 +8% TP 在此時被過濾）
        - RSI<60 同時過濾健康續漲動能（NVDA AI 主升段 RSI 常 60-75）

Att3（Based on Att1，還原 Att2 變動）—— 加入 2 日報酬上限過濾急跌進場
    變體 3a（two_day_return_cap = -0.06）：
        調整：要求 Close.pct_change(2) >= -6%（拒絕 2 日急跌 ≥ -6% 進場）
        結果：與 Att1 完全相同（34/8 訊號，Sharpe 0.41/0.96）
        分析：-6% cap **完全無綁定**——NVDA 突破+淺回檔的 2 日報酬典型
             為 -3%~-5%，極少觸及 -6%；cap 需收緊才有選擇性
    變體 3b（two_day_return_cap = -0.04）：
        調整：收緊 cap 至 -4%
        結果：
            Part A: 31 訊號, WR 64.5%, 累計 +92.36%, Sharpe **0.33**（-20% vs Att1）
            Part B:  8 訊號, WR 62.5%, 累計 +26.65%, Sharpe **0.49**（-49% vs Att1）
            min(A,B): **0.33**（三次嘗試中最差）
        失敗分析：
            - -4% cap 與 5d 淺回檔範圍 [-3%, -8%] **部分重疊**，cap 移除
              3 筆 Part A 訊號但 WR 67.6%→64.5% 下降
            - cooldown shift 效應：移除早期訊號後 shift 後續訊號觸發日期，
              Part B 2024-03-15 SL 仍存在，且新增 2024-11-29 SL -7.14%
            - 2-day return cap 方向在 momentum continuation 框架下失效：
              CIBR-012 的 cap 方向成功於 MR 策略（filter out 崩盤加速中進場），
              但 momentum continuation 的 pullback 本質就是輕度 2d 下跌，
              cap 移除的訊號與 MR 框架下的「dead-cat bounce」訊號性質不同

**三次迭代全部失敗結論**（Att1 為最佳 min 0.41，仍低於 NVDA-004 / NVDA-006 的 0.47）：

1. **Momentum Breakout Pullback Continuation 在 NVDA 上部分有效但受 regime
   依賴限制**：Part B（2024-2025 AI 牛市）Sharpe 0.96 遠勝 NVDA-004 Part B
   的 0.47（+104%），證明此結構在純趨勢期極有效；但 Part A（2019-2023）
   包含 2021 late-bull / 2022 bear / 2023 summer chop 三段問題 regime，
   突破後續漲失敗率高，Sharpe 僅 0.41。

2. **repo 第 2 次 Momentum Breakout Pullback Continuation 試驗失敗**
   （繼 FXI-012 後）：但失敗機制不同——
   - FXI-012 失敗因政策驅動 regime 轉換 + 假突破率高（Part A WR 42.3%）
   - NVDA-009 失敗因 bubble/correction 週期中的「late-cycle」突破
     （Part A WR 67.6% 已不錯，但 Sharpe 0.41 因 A/B 標準差差異）
   - 共同點：此結構需要「純上升 regime」才穩定，在多 regime 資產上
     結構性劣化於單一 regime 優化的均值回歸或突破策略

3. **Att2 / Att3 兩種精煉方向均失敗**：
   - SMA(200) regime gate：過度過濾好訊號（移除贏家多於 SL）
   - 2-day return cap filter：-6% 無綁定、-4% 雙向劣化
   - 與 Att1 baseline 相比，A/B 平衡更糟

4. **Part B 單邊優異（Sharpe 0.96）** 顯示此策略在純趨勢期有價值，
   但 min(A,B) 要求下無法勝過 NVDA-004 / NVDA-006。NVDA 高品質單邊
   趨勢期（2024-2025）以 NVDA-009 策略為補充，2019-2023 混合 regime
   期仍以 NVDA-004 BB Squeeze 或 NVDA-006 RS 框架較穩。

5. **跨資產貢獻**：Momentum Breakout Pullback Continuation 結構在 repo
   中已累積 2 個失敗資料點（FXI policy-driven / NVDA mixed-regime
   high-vol single stock），強化 cross-asset lesson：此結構只在**單一
   純上升 regime 資產**中有效，**多 regime 資產結構性劣化**。

最終參數（Att1 為 three-iteration 最佳，但仍未勝出）：
    donchian_period: 20 日
    breakout_recency_days: 10 日
    pullback_lookback: 5 日
    pullback_min: -3%（下限）
    pullback_max: -8%（上限）
    sma_trend_period: 50
    require_above_sma_long: False（Att2 嘗試過 True，失敗）
    rsi_min / rsi_max: [40, 65]
    bullish_close_required: True
    require_2d_return_cap: False（Att3 嘗試過 -6%/-4%，失敗）
    cooldown_days: 10
    出場：TP +8% / SL -7% / 20 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA009Config(ExperimentConfig):
    """NVDA-009 Momentum Breakout Pullback Continuation 參數"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 10  # 近 10 日曾創 20 日新高（NVDA 趨勢持久性）

    # Shallow pullback range (NVDA ~3.26% vol, 5% ≈ 1.5σ)
    pullback_lookback: int = 5
    pullback_min: float = -0.03  # -3% 淺回檔下限（shallow threshold）
    pullback_max: float = -0.08  # -8% 淺回檔上限（crash isolation）

    # Trend filter
    sma_trend_period: int = 50
    sma_long_period: int = 200  # Att2 試驗用：長均線 regime 過濾
    require_above_sma_long: bool = False  # Att3: 還原（Att2 過度過濾好訊號）

    # RSI neutrality filter — NVDA often runs hot, wider range
    rsi_period: int = 14
    rsi_min: float = 40.0
    rsi_max: float = 65.0  # Att3: 還原（Att2 的 60 過度過濾）

    # Bullish close confirmation
    bullish_close_required: bool = True

    # 2-day return cap filter (Att3 試驗用，CIBR-012 方向：拒絕急跌進場)
    require_2d_return_cap: bool = False  # Final（Att1）：關閉（Att3 -4%/-6% 皆劣化）
    two_day_return_cap: float = -0.06  # Att3 嘗試過 -6%（無綁定）/ -4%（劣化）

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> NVDA009Config:
    return NVDA009Config(
        name="nvda_009_momentum_pullback",
        experiment_id="NVDA-009",
        display_name="NVDA Momentum Breakout Pullback Continuation",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
