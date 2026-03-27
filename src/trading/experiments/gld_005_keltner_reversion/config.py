"""
GLD Keltner 通道均值回歸配置 (GLD Keltner Channel Mean Reversion Config)

以 Keltner Channel（EMA + ATR）取代 GLD-004 的 Bollinger Band（SMA + StdDev）。
Keltner 使用 ATR 衡量真實波動（含高低價），比標準差更穩定，且 1.5 倍 ATR
的較窄通道讓策略在溫和回調時也能觸發，提高訊號頻率。
出場沿用 GLD-004 追蹤停損機制。

Uses Keltner Channel (EMA + ATR) instead of Bollinger Bands.
ATR captures true range volatility more robustly than standard deviation.
1.5x multiplier generates more signals on moderate pullbacks.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLDKeltnerConfig(ExperimentConfig):
    """GLD Keltner 通道均值回歸參數"""

    # 進場指標
    rsi_period: int = 10
    rsi_threshold: float = 35.0
    ema_period: int = 20
    atr_period: int = 14
    keltner_multiplier: float = 1.5
    cooldown_days: int = 7

    # 追蹤停損（同 GLD-004）
    trail_activation_pct: float = 0.015
    trail_distance_pct: float = 0.01


def create_default_config() -> GLDKeltnerConfig:
    return GLDKeltnerConfig(
        name="gld_005_keltner_reversion",
        experiment_id="GLD-005",
        display_name="GLD Keltner Channel Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5%（同 GLD-004）
        stop_loss=-0.04,  # -4.0%（同 GLD-004）
        holding_days=15,  # 15 天（同 GLD-004）
    )
