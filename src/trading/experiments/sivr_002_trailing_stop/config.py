"""
SIVR 追蹤停損均值回歸配置 (SIVR Trailing Stop Mean Reversion Configuration)
進場條件同 SIVR-001，出場新增追蹤停損機制：獲利達 +2.0% 後停損跟隨最高價上移。
Entry same as SIVR-001, exit adds trailing stop: once +2.0% profit, stop trails highest price.

追蹤停損參數依 SIVR 波動率（約 GLD 的 1.5 倍）等比例放大：
- 啟動門檻：+2.0%（GLD-003 為 +1.5%）
- 追蹤距離：1.5%（GLD-003 為 1.0%）
"""

from dataclasses import dataclass

from trading.experiments.sivr_001_mean_reversion.config import SIVRMeanReversionConfig


@dataclass
class SIVRTrailingStopConfig(SIVRMeanReversionConfig):
    """SIVR 追蹤停損配置 — 繼承 SIVR-001 進場參數，新增追蹤停損出場"""

    trail_activation_pct: float = 0.02  # 獲利 +2.0% 後啟動追蹤
    trail_distance_pct: float = 0.015  # 追蹤距離 1.5%


def create_default_config() -> SIVRTrailingStopConfig:
    return SIVRTrailingStopConfig(
        name="sivr_002_trailing_stop",
        experiment_id="SIVR-002",
        display_name="SIVR Trailing Stop Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0% (同 SIVR-001)
        stop_loss=-0.045,  # -4.5% (同 SIVR-001)
        holding_days=15,  # 15 天 (同 SIVR-001)
    )
