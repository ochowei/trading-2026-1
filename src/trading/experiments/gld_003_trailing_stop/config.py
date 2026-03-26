"""
GLD 追蹤停損均值回歸配置 (GLD Trailing Stop Mean Reversion Configuration)
進場條件同 GLD-002，出場新增追蹤停損機制：獲利達 +1.5% 後停損跟隨最高價上移。
Entry same as GLD-002, exit adds trailing stop: once +1.5% profit, stop trails highest price.
"""

from dataclasses import dataclass

from trading.experiments.gld_001_mean_reversion.config import GLDMeanReversionConfig


@dataclass
class GLDTrailingStopConfig(GLDMeanReversionConfig):
    """GLD 追蹤停損配置 — 繼承 GLD-001 進場參數，新增追蹤停損出場"""
    trail_activation_pct: float = 0.015    # 獲利 +1.5% 後啟動追蹤
    trail_distance_pct: float = 0.01       # 追蹤距離 1.0%


def create_default_config() -> GLDTrailingStopConfig:
    return GLDTrailingStopConfig(
        name="gld_003_trailing_stop",
        experiment_id="GLD-003",
        display_name="GLD Trailing Stop Mean Reversion",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.025,    # +2.5% (同 GLD-002)
        stop_loss=-0.04,        # -4.0% (同 GLD-002)
        holding_days=15,        # 15 天 (同 GLD-002)
    )
