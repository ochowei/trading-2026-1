"""
VGK-002: Volatility-Adaptive RSI(2) Mean Reversion
(VGK 波動率自適應 RSI(2) 均值回歸)

基於 VGK-001 的 RSI(2) 進場架構，針對 Part A 大量停損問題：
- 加入 ATR(5)/ATR(20) > 1.15 波動率飆升過濾
  （VGK vol 1.12% ≈ XLU 1.0%，參考 XLU-011 ATR 1.15 成功案例）
- 加寬 SL 至 -3.5%（參考 DIA-005，-3.0% 太緊觸發過多停損）
- 冷卻期延長至 10 天（避免 2023-09 連續停損）
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
    close_position_threshold: float = 0.4

    # 波動率自適應過濾器（新增，參考 XLU-011）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 冷卻期（延長：5 → 10 天）
    cooldown_days: int = 10


def create_default_config() -> VGK002Config:
    return VGK002Config(
        name="vgk_002_vol_adaptive_rsi2",
        experiment_id="VGK-002",
        display_name="VGK Volatility-Adaptive RSI(2)",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 VGK-001）
        stop_loss=-0.035,  # -3.5%（加寬，參考 DIA-005）
        holding_days=20,
    )
