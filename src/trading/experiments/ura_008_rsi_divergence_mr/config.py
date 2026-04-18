"""
URA RSI Bullish Divergence + URA-004 Mean Reversion 配置 (URA-008)

基於 URA-004（10日回檔 10-20% + RSI(2) < 15 + 2日跌幅 ≤ -3%），加入 RSI(14)
bullish hook divergence 過濾器（lesson #20b，SIVR-015 Att1 驗證），捕捉「RSI 已從
oversold 低點回升」的 capitulation 尾聲訊號，移除「RSI 仍在下探」的持續下跌訊號。

Hypothesis: URA-004 Part A 22 筆訊號中的 7 筆停損部分源自 RSI(14) 仍在下探中的
「falling knife」情境，加入 RSI(14) hook divergence 可選擇性移除這些訊號。

URA 形式上符合 lesson #20b 全部四項條件：
  - 日波動 2.34%（2-3% 範圍）
  - 已驗證 pullback+RSI(2) 均值回歸框架（URA-004）
  - Pullback lookback 10 日（≤10 日要求）
  - URA-004 Part A Sharpe 0.41 / Part B 0.39（兩段活躍 MR regime）

Based on URA-004, adds RSI(14) bullish hook filter (simplified classical bullish
divergence): requires RSI(14) to have risen from recent 5-day low by ≥ H points
where the low itself was ≤ 35 (oversold context).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URARSIDivergenceMRConfig(ExperimentConfig):
    """URA RSI Bullish Divergence + URA-004 均值回歸參數"""

    # 進場指標（同 URA-004）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔 ≤ 20%
    rsi2_period: int = 2
    rsi2_threshold: float = 15.0  # RSI(2) < 15
    two_day_decline: float = -0.03  # 2日跌幅 ≤ -3%

    # 新增：RSI(14) bullish hook 過濾（移植 SIVR-015 Att1 參數）
    rsi_period: int = 14
    rsi_hook_lookback: int = 5  # 觀察過去 N 日內 RSI 最低點
    rsi_hook_delta: float = 3.0  # RSI 需自近期低點回升 ≥ H 點
    rsi_hook_max_min: float = 35.0  # 近期 RSI 低點須曾 ≤ 此水位（oversold）

    cooldown_days: int = 10


def create_default_config() -> URARSIDivergenceMRConfig:
    return URARSIDivergenceMRConfig(
        name="ura_008_rsi_divergence_mr",
        experiment_id="URA-008",
        display_name="URA RSI Bullish Divergence + Pullback+RSI(2)+2DD MR",
        tickers=["URA"],
        data_start="2010-11-05",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.055,  # -5.5%
        holding_days=20,
    )
