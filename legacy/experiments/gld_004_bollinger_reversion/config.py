"""
GLD 布林帶均值回歸配置 (GLD Bollinger Band Mean Reversion Configuration)
以布林帶取代固定 SMA 乖離閾值，動態適應波動度。RSI 放寬至 35，冷卻縮短至 7 天。
出場沿用 GLD-003 追蹤停損機制。

Uses Bollinger Bands (adaptive to volatility) instead of fixed SMA deviation.
RSI relaxed to 35, cooldown shortened to 7 days. Exit uses GLD-003's trailing stop.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLDBollingerReversionConfig(ExperimentConfig):
    """GLD 布林帶均值回歸參數"""

    # 進場指標
    rsi_period: int = 10
    rsi_threshold: float = 35.0
    bb_period: int = 20
    bb_std: float = 2.0
    cooldown_days: int = 7

    # 追蹤停損
    trail_activation_pct: float = 0.015  # 獲利 +1.5% 後啟動追蹤
    trail_distance_pct: float = 0.01  # 追蹤距離 1.0%


def create_default_config() -> GLDBollingerReversionConfig:
    return GLDBollingerReversionConfig(
        name="gld_004_bollinger_reversion",
        experiment_id="GLD-004",
        display_name="GLD Bollinger Band Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.025,  # +2.5% (同 GLD-003)
        stop_loss=-0.04,  # -4.0% (同 GLD-003)
        holding_days=15,  # 15 天 (同 GLD-003)
    )
