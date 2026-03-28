"""
USO 收緊出場 + 短持倉均值回歸配置 (USO-005)

基於 USO-001，調整出場參數：
1. 停損從 -3.5% 收緊至 -3.25%，降低單筆損失幅度
2. 持倉從 15 天縮短至 10 天（USO-001 平均持倉僅 2.4-3.4 天，15 天多餘）
進場條件與 USO-001 完全相同。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOSymmetricTightConfig(ExperimentConfig):
    """USO 收緊出場 + 短持倉參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 回檔 ≥6%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    cooldown_days: int = 10


def create_default_config() -> USOSymmetricTightConfig:
    return USOSymmetricTightConfig(
        name="uso_005_symmetric_tight",
        experiment_id="USO-005",
        display_name="USO Tight Exit + Short Holding",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,  # +3.0%
        stop_loss=-0.0325,  # -3.25% (USO-001 為 -3.5%)
        holding_days=10,  # 10 天 (USO-001 為 15 天)
    )
