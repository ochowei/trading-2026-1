"""
VGK-002: Volatility-Adaptive RSI(2) Mean Reversion
(VGK 波動率自適應 RSI(2) 均值回歸)

基於 VGK-001 RSI(2) 進場架構，加入 ATR(5)/ATR(20) 波動率飆升過濾。
VGK Part A 在 2022 歐洲能源危機/俄烏戰爭期間因緩跌連續停損，
ATR 過濾可區分「急跌恐慌」與「緩跌磨損」，移除後者。

參數邏輯：
- ATR > 1.15：參考 XLU-011 成功經驗（XLU 1.0% vol → 1.15 甜蜜點）
  VGK 1.12% vol 接近 XLU，選用 1.15 作為起點
- 其餘參數同 VGK-001 / SPY-005（TP +3.0%, SL -3.0%, 20d hold）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK002Config(ExperimentConfig):
    """VGK-002 波動率自適應 RSI(2) 均值回歸參數"""

    # RSI(2) 參數（同 VGK-001）
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10

    # 2 日累計跌幅過濾（同 VGK-001）
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（同 VGK-001）
    close_position_threshold: float = 0.4  # >= 40%

    # 波動率自適應過濾器（新增）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15  # XLU-011 甜蜜點（1.1-1.15 結果相同）

    # 冷卻期（同 VGK-001）
    cooldown_days: int = 5


def create_default_config() -> VGK002Config:
    return VGK002Config(
        name="vgk_002_vol_adaptive_rsi2",
        experiment_id="VGK-002",
        display_name="VGK Volatility-Adaptive RSI(2)",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 VGK-001）
        stop_loss=-0.030,  # -3.0%（同 VGK-001 / SPY-005）
        holding_days=20,  # 20 天（同 VGK-001）
    )
