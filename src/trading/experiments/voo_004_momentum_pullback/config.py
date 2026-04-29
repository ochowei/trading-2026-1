"""
VOO-004: Momentum Breakout Pullback Continuation (MBPC)

動機（Motivation）：
    VOO 目前全域最優為 VOO-003 RSI(2) Mean Reversion（min(A,B) 0.53）。
    repo 在 VOO 上僅累積 3 次實驗（VOO-001/002/003），全部為 RSI(2) MR
    框架的出場參數調整，**進場結構從未被探索**。

    本實驗探索 repo 中較少使用的「趨勢跟蹤 / 動量連續」方向。

    跨資產 lesson #21（cross_asset_lessons.md）明確假設：
    "MBPC 可能在單一結構性上升趨勢資產（如 SPY 2023-2025、VOO、DIA）中有效；
     在週期性 / 事件驅動 / 多 regime 資產（FXI、URA、TLT、INDA、EEM、NVDA、FCX）
     中結構性劣化"

    **VOO 為純結構性上升趨勢資產**（S&P 500 自 2010 ETF 上市以來年化
    +12-13%，2019-2025 期間僅 2020-03 COVID、2022 升息熊市兩個顯著回撤
    regime，相對 NVDA/FXI 多 regime 結構單純）。本實驗為 lesson #21
    跨資產假設的直接驗證——若 MBPC 在 VOO 上有效，將擴展 lesson 至
    "broad-uptrend ETF" 類別。

    與 NVDA-009 的關鍵差異：
    - VOO 日波動 ~1.0-1.2% vs NVDA 3.26%（約 1/3）
    - 參數縮放：pullback 範圍 / TP / SL / 滑價皆按 lesson #7 縮放
    - VOO 為廣基 ETF，無個股泡沫週期（NVDA 2021 late-bull SL 集中問題不適用）

策略方向：趨勢跟蹤 / 動量連續（Trend-following / Momentum Continuation）
    捕捉 VOO 強趨勢中的「Donchian 新高 → 淺回檔 → 多頭 K 棒確認」連續模式。

進場條件（Entry conditions）：
    1. 近 N 日內曾創 Donchian 20 日新高（breakout freshness）
    2. Close > SMA(50)（中期趨勢向上）
    3. 當前 Close 相對於 5 日高點回檔在 [pullback_max, pullback_min] 範圍
       （淺回檔 -1.5% ~ -4%，VOO 1.0% vol 下 -3% ≈ 3σ）
    4. RSI(14) ∈ [rsi_min, rsi_max]（非深度超賣，亦非過熱）
    5. Close > Open（當日多頭 K 棒確認）
    6. 冷卻 10 個交易日

出場條件（Exit conditions）：
    - TP +3.0%（VOO-003 驗證 +2.85% 為 RSI(2) MR 甜蜜點，
      MBPC 進場時機通常在新高後淺回檔，續漲幅度典型 2-3%；採稍寬 +3.0%）
    - SL -2.5%（MBPC 不應深度逆向，較 VOO-003 MR 的 -3.0% 更緊；
      逆向超 -2.5% 通常意味突破失敗）
    - 最長持倉 20 天
    - 滑價 0.10%（VOO 標準）
    - 悲觀認定：是

成交模型（Execution Model）：
    - 進場：隔日開盤市價（next_open_market）
    - 止盈：限價賣單 Day（limit_order_day）
    - 停損：停損市價 GTC（stop_market_gtc）
    - 到期：隔日開盤市價

迭代歷程（Iteration Log）：

Att1（Baseline）—— Donchian 新高 + 淺回檔 + SMA(50) + RSI [40,60]
    進場：
        1. 近 10 日內曾創 20 日 Donchian 新高
        2. Close > SMA(50)
        3. 5 日高點回檔在 [-1.5%, -4%]
        4. RSI(14) ∈ [40, 60]
        5. Close > Open
        6. 冷卻 10 日
    出場：TP +3.0% / SL -2.5% / 20 天
    結果：
        Part A: 19 訊號, WR 52.6%, 累計 +6.02%, Sharpe **0.12**
        Part B: 10 訊號, WR 60.0%, 累計 +9.42%, Sharpe **0.36**
        min(A,B): **0.12**（遠低於 VOO-003 的 0.53）
    Part A 失敗分析：
        - 9 筆 SL：2019-05（Fed pivot）/ 2020-05 / 2020-10（election）/
          2021-11（Omicron）/ 2022-01 / 2022-04 / 2022-08（Jackson Hole 鷹派）/
          2023-02（Powell 鷹派）/ 2023-08（Fitch 下調）
        - 5/9 集中於 macro-shock 日，突破後反轉觸 SL
        - WR 52.6% 在多 regime 期顯示框架偽訊號率高

Att2（Based on Att1）—— + SMA(200) regime gate（NVDA-009 Att2 方向）
    調整：require_above_sma_long = True
    結果：
        Part A: 15 訊號, WR 53.3%, 累計 +5.34%, Sharpe **0.14**
        Part B:  9 訊號, WR 55.6%, 累計 +6.23%, Sharpe **0.27**
        min(A,B): **0.14**（marginal +0.02 vs Att1，仍遠低於 VOO-003）
    失敗分析：
        - SMA(200) 為非選擇性過濾（與 NVDA-009 Att2 相同）
        - Part A 訊號 -21% 但 WR 僅 +0.7pp
        - Part B 訊號 -10%，WR -4.4pp（移除 winners）
        - SMA(200) 在 2022 bear 期被跌破時，bull-trap rallies
          仍可能達到 +3% TP（如 VOO 2022-11-07/12-08），Att2 將其過濾
        - repo 第 2 次驗證 SMA(200) regime gate 在 MBPC 框架下非選擇性失敗

Att3 ★（Based on Att1，還原 Att2 變動）—— 收緊 breakout recency + 窄帶 pullback range
    調整：
        - breakout_recency_days: 10 → 5（要求新鮮 Donchian 突破）
        - pullback range: [-1.5%, -4%] → [-2%, -3%]（窄帶 pullback）
        - require_above_sma_long: False（還原 Att2）
    結果：
        Part A: 7 訊號, WR 85.7%, 累計 +16.30%, Sharpe **1.12**
        Part B: 2 訊號, WR 100%（2/2 全達標 +3.00%）, 累計 +6.09%, Sharpe **0.00 std=0**
        min(A,B): **1.12†**（Part A 為約束，沿用 EWJ-003 / DIA-012 / SPY-009 慣例）
    A/B 平衡（user 要求 cum<30% / 訊號<50%）：
        - 年化 cum 差: 3.07%/y vs 3.00%/y → **2.3% gap**（< 30% ✓ 極佳）
        - 年化訊號比: 1.4/y vs 1.0/y → **28.6% gap**（< 50% ✓）
    Part A 改善：
        - 9 筆 macro-shock SL 中 8 筆被過濾，僅保留 2022-01-10（真實 bear 開端）
        - 7 筆 TP 結構：2019-03×2 / 2019-12 / 2020-01 / 2021-01 / 2021-05 / 2022-11
        - WR 52.6% → 85.7%（+33pp）

**三次迭代結論（Att3 為新最佳）**：

1. **MBPC 結構在 VOO 上有效**（repo 第 3 次 MBPC 試驗，首次成功）
   驗證 cross_asset_lesson #21 假設：「MBPC 可能在單一結構性上升趨勢資產
   （如 SPY 2023-2025、VOO、DIA）中有效；在週期性 / 事件驅動 / 多 regime
   資產（FXI、URA、TLT、INDA、EEM、NVDA、FCX）中結構性劣化」
   - 失敗：NVDA-009（多 regime 個股）、FXI-012（政策驅動 EM）
   - 成功：VOO-004 Att3（純 broad-uptrend ETF）

2. **進場品質精煉 >> regime 閘門**：Att2 SMA(200) 失敗、Att3 收緊
   pullback range + breakout recency 成功。MBPC 框架的最佳精煉方向為
   **訊號層精煉**（recency + 窄帶 pullback），而非 **regime 層過濾**

3. **跨資產規則擴展（lesson #21 + lesson #4 進場參數敏感度）**：
   MBPC 進場參數對 Sharpe 影響極大——breakout_recency 從 10→5 + pullback
   range 從 [-1.5,-4] 收緊至 [-2,-3]，min(A,B) 從 0.12→1.12（+833%）。
   呼應 lesson #4：進場條件改動對績效影響 3-5 倍於出場參數

4. **樣本警告**：Part B 2 訊號（1.0/年）統計顯著性偏低，但與 VOO-003
   Part B 4 訊號同數量級。框架在 2022-01-10 hawkish Fed 仍有 1 筆 SL，
   未來 bear regime 開端進場有風險，但屬可接受範圍

最終參數（Att3）：
    donchian_period: 20
    breakout_recency_days: 5
    pullback_lookback: 5
    pullback_min: -2%
    pullback_max: -3%
    sma_trend_period: 50
    require_above_sma_long: False
    rsi_min / rsi_max: [40, 60]
    bullish_close_required: True
    cooldown_days: 10
    出場：TP +3.0% / SL -2.5% / 20 天，滑價 0.10%，悲觀認定 True
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOO004Config(ExperimentConfig):
    """VOO-004 Momentum Breakout Pullback Continuation 參數"""

    # Donchian breakout freshness (Att3: 10 → 5 收緊新鮮度)
    donchian_period: int = 20
    breakout_recency_days: int = 5  # 近 5 日曾創 20 日新高（Att3 收緊）

    # Shallow pullback range (Att3: 收緊至 -2% ~ -3% 排除邊緣 pullback)
    pullback_lookback: int = 5
    pullback_min: float = -0.02  # -2% 淺回檔下限（Att3 收緊自 -1.5%）
    pullback_max: float = -0.03  # -3% 淺回檔上限（Att3 收緊自 -4%）

    # Trend filter
    sma_trend_period: int = 50
    sma_long_period: int = 200
    require_above_sma_long: bool = False  # Att3: 還原（Att2 非選擇性失敗）

    # RSI neutrality filter
    rsi_period: int = 14
    rsi_min: float = 40.0
    rsi_max: float = 60.0

    # Bullish close confirmation
    bullish_close_required: bool = True

    # ATR ratio filter (Att3 試驗用，過濾低品質慢磨突破)
    require_atr_ratio: bool = False
    atr_ratio_min: float = 1.0  # ATR(5)/ATR(20) >= X

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> VOO004Config:
    return VOO004Config(
        name="voo_004_momentum_pullback",
        experiment_id="VOO-004",
        display_name="VOO Momentum Breakout Pullback Continuation",
        tickers=["VOO"],
        data_start="2010-10-01",
        profit_target=0.030,  # +3.0%
        stop_loss=-0.025,  # -2.5%
        holding_days=20,
    )
