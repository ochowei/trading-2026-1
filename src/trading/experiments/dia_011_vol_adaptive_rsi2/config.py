"""
DIA-011: Volatility-Adaptive RSI(2) Mean Reversion
(DIA 波動率自適應 RSI(2) 均值回歸)

基於 DIA-005 的 RSI(2) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾。
靈感來自 IWM-011（min Sharpe +67.7%）和 XLU-011（+272%）的成功案例。

假說：ATR > 1.1 可區分急跌恐慌（快速反彈）和慢磨下跌（容易停損），
移除低品質訊號以提升 Sharpe ratio。

結果：3 次嘗試均未能超越 DIA-005（min Sharpe 0.47）：
  Att1: ATR>1.1/SL-3.5% → Part A 0.45/Part B 0.47, min 0.45（移除 5 贏 1 輸）
  Att2: ATR>1.05/SL-3.5% → Part A 0.32/Part B 0.47, min 0.32（引入壞訊號）
  Att3: ATR>1.1/SL-4.0% → Part A 0.87/Part B 0.40, min 0.40（A/B gap 0.47）
結論：DIA 日波動 ~1.0% 使 RSI(2) 訊號跨波動率制域均有效，ATR 過濾無法區分好壞。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA011Config(ExperimentConfig):
    """DIA-011 波動率自適應 RSI(2) 均值回歸參數"""

    # RSI(2) 參數（同 DIA-005）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 DIA-005）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 DIA-005）
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1

    # 冷卻期（同 DIA-005）
    cooldown_days: int = 5


def create_default_config() -> DIA011Config:
    return DIA011Config(
        name="dia_011_vol_adaptive_rsi2",
        experiment_id="DIA-011",
        display_name="DIA Volatility-Adaptive RSI(2)",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 DIA-005）
        stop_loss=-0.035,  # -3.5%（同 DIA-005，Att1 最佳 min Sharpe）
        holding_days=25,  # 25 天（同 DIA-005）
    )
