"""
IWM-014: Momentum Breakout Pullback Continuation (MBPC)

策略方向：趨勢跟蹤 / 動量連續（Trend-following / Momentum Continuation）。
Repo 中相對較少使用的方向（過往 IWM 13 次實驗中僅 IWM-007 SMA pullback /
IWM-009 RS momentum 兩次趨勢類嘗試，皆失敗——但兩者均為「趨勢回檔 MR」結構，
非「動量延續」結構，本實驗為 IWM 首次純 MBPC 框架）。

動機（Motivation）：
    IWM 目前全域最優 IWM-013 Att3 (Capitulation-Depth Filter MR, RSI(2)<8)
    min(A,B) 0.59，Part B std=0（3 訊號全達 +4% TP，零方差）為結構性壓縮。
    IWM-013 之前的 IWM-006/008 BB Squeeze Breakout 嘗試 min(A,B) 僅 0.31，
    Part A 9 SLs 主要在 2019-2021 mid-uptrend false breakouts。

    Trade-level analysis（IWM-006 baseline）顯示：
      - Part A SLs SMA20/SMA60 ratio 分布 1.013-1.084（5 訊號）
      - Part A TPs 分布 0.943-1.095（8 訊號，4 筆 ratio<1.0 為 post-bear
        transition winners，4 筆 1.04-1.10 為 mid-uptrend winners）
      - SLs 與 TPs 在 ratio 維度高度重疊，**lesson #22 BOX 結構性失效**

    pivot 至 lesson #21 MBPC 框架（Donchian 新高 → 淺回檔 → 多頭 K 棒），
    跨資產驗證假設：「MBPC 在 broad-uptrend ETF 類別中有效」（VOO-004 Att3
    1.12 為唯一驗證點，IWM-014 為第二個 broad-uptrend ETF 試驗）。

    與 VOO 的關鍵差異：
    - IWM 日波動 ~1.5-2% vs VOO ~1.0-1.2%（約 1.5x）
    - 參數縮放（依 lesson #7 波動度縮放法則）：
        pullback range: VOO [-2%,-3%] → IWM [-3%,-4.5%]
        TP: VOO +3.0% → IWM +4.5%
        SL: VOO -2.5% → IWM -3.75%
        滑價: 0.10%（兩者相同，IWM 流動性同樣高）
    - IWM 為 Russell 2000 small cap broad ETF，有「個股事件聚合」噪音
      （IWM-012 失敗根因），可能需要更精細的進場確認

策略方向：趨勢跟蹤 / 動量連續
    捕捉 IWM 強趨勢中的「Donchian 新高 → 淺回檔 → 多頭 K 棒確認」連續模式。

進場條件（Entry conditions）：
    1. 近 N 日內 High 曾突破前 20 日最高（breakout freshness）
    2. Close > SMA(50)（中期趨勢向上）
    3. 當前 Close 相對於 5 日高點回檔在 [pullback_max, pullback_min] 範圍
    4. RSI(14) ∈ [rsi_min, rsi_max]（非深度超賣，亦非過熱）
    5. Close > Open（當日多頭 K 棒確認）
    6. 冷卻 cooldown_days 個交易日

出場條件（Exit conditions）：
    - TP +4.5%（VOO +3% 按 1.5x 縮放）
    - SL -3.75%（VOO -2.5% 按 1.5x 縮放）
    - 最長持倉 20 天
    - 滑價 0.10%
    - 悲觀認定：是

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價

迭代歷程（Iteration Log）：

Att1 — VOO-004 Att3 vol-scaled baseline (FAILED, min(A,B)=0.00)
    進場：
        donchian=20, recency=5, pullback=[-3%,-4.5%], RSI[40,60],
        Close>SMA(50), Close>Open, cd=10
    出場：TP+4.5% / SL-3.75% / 20 天
    結果：
        Part A: 3 訊號 WR 0% Sharpe 0.00（formal）, cum -11.11%
            - 2019-05-10 SL（trade war escalation）
            - 2021-03-22 SL（post-stimulus rates spike）
            - 2022-11-18 SL（mid-2022 bear）
        Part B: 4 訊號 WR 75% Sharpe 0.67, cum +9.72%
        min(A,B): **0.00**（Part A 為瓶頸，3/3 SLs 全為 macro-shock 日）
    分析：
        - 訊號密度過低（Part A 0.6/yr）使統計不可靠
        - Part A 3 SLs 全為 macro-shock，框架本身在 macro-stable Part B
          有效但無法區分 macro-event 訊號
        - VOO-004 Att3 的緊參數移植至 IWM 後過嚴——IWM 1.5x 波動使得
          [-3%,-4.5%] 範圍訊號稀少。需放寬

Att2 — Looser entry（FAILED, min(A,B)=-0.38）
    調整：
        - recency: 5 → 10（捕捉更多 breakout pullback 機會）
        - pullback range: [-3%,-4.5%] → [-2%,-5%]（更寬範圍）
        - RSI: [40,60] → [40,65]
    結果：
        Part A: 20 訊號 WR 30%, Sharpe **-0.38**, cum -25.97%
        Part B: 13 訊號 WR 46.2%, Sharpe **0.02**, cum +0.10%
        min(A,B): **-0.38**（嚴重崩壞，比 Att1 更糟）
    分析：
        - 放寬 entry 在 IWM 上引入大量低品質 breakout pullback（30% WR）
        - 與 VOO 不同：VOO 寬-tight 兩端皆有訊號，IWM 寬端訊號品質崩壞
        - 印證 IWM 為 small-cap broad ETF（個股事件聚合）的結構性特性
        - lesson #4 進場敏感度反向案例：放寬使品質崩壞 3-5 倍

Att3 — Att1 tight + ATR ratio filter + 中度 RSI 收緊（FAILED, min(A,B)=0.00）
    調整 vs Att1：
        - 還原 recency=5, pullback=[-3%,-4.5%], 維持 Att1 緊框架
        - require_atr_ratio = True, atr_ratio_min = 1.10
        - RSI: [40,60] → [42,58]
    結果：
        Part A: 1 訊號 WR 0%, Sharpe **0.00**, 1 SL
        Part B: 1 訊號 WR 0%, Sharpe **0.00**, 1 SL
        min(A,B): **0.00**（過度收緊，唯一保留訊號為兩段 SL）
    分析：
        - ATR>1.10 + RSI[42,58] + 緊 pullback 三重交集過濾過嚴
        - 訊號密度崩潰至 0.4/yr，統計無意義
        - 與 IWM-008 BB Squeeze 過度優化失敗模式同類

================================================================================
三次迭代總結（IWM-014 全部失敗）：
================================================================================

| Att | 進場 | Part A 訊號 | Part A WR | Part A Sharpe | Part B Sharpe | min(A,B) |
|-----|------|------------|----------|---------------|---------------|----------|
| 1   | Tight (VOO Att3 vol-scaled) | 3 | 0% | 0.00 | 0.67 | **0.00** |
| 2   | Loose | 20 | 30% | -0.38 | 0.02 | **-0.38** |
| 3   | Tight + ATR + RSI tight | 1 | 0% | 0.00 | 0.00 | **0.00** |

vs IWM-013 Att3 (current global optimum) min(A,B) **0.59**：所有 3 次迭代均嚴重劣於基準。

核心失敗根因：
1. **MBPC 框架在 IWM 上結構性失效**：擴展 lesson #21 失敗家族至「小型股
   寬基 ETF」（mixed regimes + 個股事件聚合）。Repo 第 4 次 MBPC 試驗
   （前 3 次：VOO-004 ★成功、NVDA-009 失敗、FXI-012 失敗、NVDA-013 ★成功
   配 lesson #22 regime gate）。
2. **波動度縮放（VOO 1.0% → IWM 1.5%）對 entry 參數有效性下降**：
   VOO-004 Att3 緊參數移植至 IWM 後訊號密度過低（0.6/yr）；放寬則品質崩壞。
   IWM 的 small-cap event-aggregation noise 結構使 MBPC pullback signals
   無法清晰區分「genuine continuation」與「macro-shock false breakout」。
3. **進場敏感度反向案例（lesson #4 反例）**：VOO 上 entry tight→loose 翻
   轉 1.12→0.12（Sharpe 9 倍差距）；IWM 上 tight→loose 翻轉 0.00→-0.38。
   兩者都顯示進場敏感度，但 IWM 的「最佳訊號帶」在當前 MBPC 框架內可能
   不存在——3 次迭代都未找到正 Sharpe 區間。
4. **trade-level SMA20/SMA60 ratio 分析**：IWM-006 baseline trades 顯示
   Part A SLs (1.013-1.084) 與 TPs (0.943-1.095) 在 ratio 維度高度重疊
   （4 TPs 在 transition zone <1.00, 4 TPs 在 mid-uptrend 1.04-1.10），
   lesson #22 BOX 也結構性無效（即未進入本實驗測試的次要備案）。

新跨資產規則（lesson #21 family 精煉）：
**MBPC（Donchian breakout + shallow pullback continuation）框架在「小型
股寬基 ETF」上結構性失效**——即使按波動度比例縮放並嘗試多重收緊/放寬
組合。**MBPC 適用範圍重新定義為「single-pure-uptrend 大型廣基 ETF」
（VOO/SPY/DIA 類）或「single-regime growth 個股配 lesson #22 regime
gate」（NVDA-013）；不適用 small-cap broad ETF（IWM 為新失敗數據點）、
policy-driven EM (FXI)、mixed-regime 個股（NVDA-009 純 MBPC）**。

IWM-013 Att3（RSI(2)<8 capitulation-depth filter MR）仍為 IWM 全域最優
（14 次實驗、46+ 次嘗試）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM014Config(ExperimentConfig):
    """IWM-014 Momentum Breakout Pullback Continuation 參數"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 5  # Att3: 還原 Att1

    # Shallow pullback range（vol-scaled vs VOO）
    pullback_lookback: int = 5
    pullback_min: float = -0.030  # Att3: 還原 Att1 -3%
    pullback_max: float = -0.045  # Att3: 還原 Att1 -4.5%

    # Trend filter
    sma_trend_period: int = 50
    sma_long_period: int = 200
    require_above_sma_long: bool = False

    # RSI neutrality filter
    rsi_period: int = 14
    rsi_min: float = 42.0  # Att3: 40→42 略緊
    rsi_max: float = 58.0  # Att3: 60→58 略緊

    # Bullish close confirmation
    bullish_close_required: bool = True

    # Optional ATR ratio filter (Att3 啟用)
    require_atr_ratio: bool = True
    atr_ratio_min: float = 1.10  # ATR(5)/ATR(20) >= 1.10

    # Optional buffered multi-week SMA regime gate (lesson #22)
    require_sma_regime: bool = False
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.95
    sma_regime_ratio_max: float = 1.10

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> IWM014Config:
    """建立預設配置（Att1 baseline）"""
    return IWM014Config(
        name="iwm_014_momentum_pullback",
        experiment_id="IWM-014",
        display_name="IWM Momentum Breakout Pullback Continuation",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.045,  # +4.5% (VOO +3% × 1.5)
        stop_loss=-0.0375,  # -3.75% (VOO -2.5% × 1.5)
        holding_days=20,
    )
