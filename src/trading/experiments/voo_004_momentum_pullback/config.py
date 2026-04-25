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

[填入] Att1 Baseline / Att2 / Att3
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOO004Config(ExperimentConfig):
    """VOO-004 Momentum Breakout Pullback Continuation 參數"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 10  # 近 10 日曾創 20 日新高

    # Shallow pullback range (VOO ~1.0% vol, -3% ≈ 3σ)
    pullback_lookback: int = 5
    pullback_min: float = -0.015  # -1.5% 淺回檔下限（避免過淺進場）
    pullback_max: float = -0.04  # -4% 淺回檔上限（隔離崩盤前下跌）

    # Trend filter
    sma_trend_period: int = 50
    sma_long_period: int = 200  # Att2 試驗用：長均線 regime 過濾
    require_above_sma_long: bool = True  # Att2: 啟用

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
