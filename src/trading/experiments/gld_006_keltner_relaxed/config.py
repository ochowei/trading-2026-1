"""
GLD 放寬 Keltner 通道均值回歸配置 (GLD Relaxed Keltner Channel Mean Reversion Config)

基於 GLD-005 的 Keltner Channel (EMA20 - 1.5xATR14)，放寬進場條件：
1. RSI(10) 閾值從 35 放寬至 37
2. 冷卻期從 7 天縮短為 3 天

此改變能大幅增加訊號數量，讓 Part A 及 Part B 的訊號數跟隨時間長度比例更為接近，
並提升整體的累計報酬，讓 Part A 訊號從 33 次提升至 60 次，Part B 訊號從 3 次提升至 6 次。

Uses Keltner Channel (EMA20 + 1.5xATR14) but with relaxed RSI threshold (37)
and shortened cooldown (3 days) to increase signal frequency and total return.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLDRelaxedKeltnerConfig(ExperimentConfig):
    """GLD 放寬 Keltner 通道均值回歸參數"""

    # 進場指標
    rsi_period: int = 10
    rsi_threshold: float = 37.0  # 放寬至 37.0 (GLD-005: 35.0)
    ema_period: int = 20
    atr_period: int = 14
    keltner_multiplier: float = 1.5
    cooldown_days: int = 3  # 縮短至 3 天 (GLD-005: 7 天)

    # 追蹤停損（同 GLD-004/005）
    trail_activation_pct: float = 0.015
    trail_distance_pct: float = 0.01


def create_default_config() -> GLDRelaxedKeltnerConfig:
    return GLDRelaxedKeltnerConfig(
        name="gld_006_keltner_relaxed",
        experiment_id="GLD-006",
        display_name="GLD Relaxed Keltner Channel Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（同 GLD-004/005）
        stop_loss=-0.04,  # -4.0%（同 GLD-004/005）
        holding_days=15,  # 15 天（同 GLD-004/005）
    )
