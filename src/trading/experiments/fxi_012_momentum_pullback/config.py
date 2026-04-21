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
        - RSI 範圍收緊 [45, 58]（排除過度回檔和超買邊界）
        - 其他條件保持
    預期效果：
        - Part A 熊市反彈訊號將被 SMA(20)>SMA(50) 濾除
        - Part B 真正上升趨勢保留
        - 訊號總數減少但品質提升

Att3（待定）：基於 Att2 結果微調

核心參數（Att2 當前）：
    pullback_lookback: 5 日
    pullback_min: -0.02（2% 淺回檔下限）
    pullback_max: -0.05（5% 淺回檔上限）
    donchian_period: 20 日
    breakout_recency_days: 5
    sma_short_period: 20（Att2 新增：短均線）
    sma_trend_period: 50
    require_sma20_above_sma50: True（Att2 新增：黃金排列）
    rsi_period: 14
    rsi_min: 45（Att2 收緊）
    rsi_max: 58（Att2 收緊）
    cooldown_days: 10
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI012Config(ExperimentConfig):
    """FXI-012 Momentum Breakout Pullback Continuation 參數（Att2）"""

    # Donchian breakout freshness
    donchian_period: int = 20
    breakout_recency_days: int = 5

    # Shallow pullback range
    pullback_lookback: int = 5
    pullback_min: float = -0.02  # -2% 淺回檔下限
    pullback_max: float = -0.05  # -5% 淺回檔上限

    # Trend filter (Att2: 雙均線黃金排列)
    sma_short_period: int = 20
    sma_trend_period: int = 50
    require_sma20_above_sma50: bool = True

    # RSI neutrality filter (Att2: 收緊 [45, 58])
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
        profit_target=0.04,  # +4.0%（動量連續中等目標）
        stop_loss=-0.035,  # -3.5%（淺回檔上方停損）
        holding_days=15,  # 15 天
    )
