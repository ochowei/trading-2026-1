"""
SIVR RSI Bullish Divergence + Pullback+WR Mean Reversion 配置 (SIVR-015)

基於 SIVR-005（pullback 7-15% + WR(10) ≤ -80），加入 RSI(14) 多頭動能轉折（bullish hook）
過濾器。classical bullish divergence 的簡化版：要求 RSI(14) 已從近期低點回升若干點，
藉此過濾「RSI 仍在下跌中的訊號日」（持續下跌結構），保留「RSI 已轉折但價格仍淺超賣」
（capitulation 尾聲）訊號。

Hypothesis: SIVR-005 Part A WR 62.5%（12 stop-outs in 32 trades）裡有部分訊號是在
RSI 仍在下探中觸發（prolonged decline），bullish hook 過濾器可選擇性移除這些訊號。

尚未在 repo 中任何資產測試 classical divergence 形式（SIVR-007 為 20d lookback，非真正 divergence；
SIVR-007 Att1 的 "RSI(14) momentum recovery filter" 使用 5-day RSI minimum 為 reference，
但搭配 20日 pullback 且未使用 hook 閾值）。

Based on SIVR-005 (pullback 7-15% + WR(10) ≤ -80), adds an RSI(14) bullish hook filter
(simplified classical bullish divergence): requires RSI(14) to have risen from its
recent low by at least H points, so as to filter out signals where RSI is still
declining (prolonged downtrend) while keeping "RSI turned but price still oversold"
(capitulation end) signals.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRRSIDivergenceMRConfig(ExperimentConfig):
    """SIVR RSI Bullish Divergence + Pullback+WR 均值回歸參數"""

    # 進場指標（同 SIVR-005）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_cap: float = -0.15  # 回檔 ≤ 15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 新增：RSI(14) bullish hook 過濾（Att1 為全域最優，三次迭代詳見 docs）
    rsi_period: int = 14
    rsi_hook_lookback: int = 5  # 觀察過去 N 日內 RSI 最低點
    rsi_hook_delta: float = 3.0  # RSI 需自近期低點回升 ≥ H 點
    rsi_hook_max_min: float = 35.0  # 近期 RSI 低點須曾 ≤ 此水位（oversold）

    cooldown_days: int = 10


def create_default_config() -> SIVRRSIDivergenceMRConfig:
    return SIVRRSIDivergenceMRConfig(
        name="sivr_015_rsi_divergence_mr",
        experiment_id="SIVR-015",
        display_name="SIVR RSI Bullish Divergence + Pullback+WR MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,
    )
