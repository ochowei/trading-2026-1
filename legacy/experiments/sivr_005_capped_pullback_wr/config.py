"""
SIVR 回檔範圍 + Williams %R 均值回歸配置
(SIVR Capped Pullback + Williams %R Mean Reversion Config)

基於 SIVR-003，加入回檔上限 15% 過濾極端崩盤訊號。
參考 USO-010→012→013 的回檔範圍過濾成功經驗。
極端回檔（如 2020 COVID -28%）產生低品質均值回歸訊號。

Based on SIVR-003, adds pullback cap at 15% to filter extreme crash signals.
Inspired by USO series success with pullback range filtering.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRCappedPullbackWRConfig(ExperimentConfig):
    """SIVR 回檔範圍 + Williams %R 均值回歸參數"""

    # 進場指標（同 SIVR-003 + 回檔上限）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%
    pullback_cap: float = -0.15  # 回檔 ≤15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> SIVRCappedPullbackWRConfig:
    return SIVRCappedPullbackWRConfig(
        name="sivr_005_capped_pullback_wr",
        experiment_id="SIVR-005",
        display_name="SIVR Capped Pullback + Williams %R Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,  # 15 天
    )
