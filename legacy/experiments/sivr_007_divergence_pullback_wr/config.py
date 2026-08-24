"""
SIVR 20日回檔範圍 + Williams %R 均值回歸配置
(SIVR 20-Day Capped Pullback + Williams %R Mean Reversion Config)

基於 SIVR-005，將回檔回看窗口從 10 日擴展至 20 日。
參考 COPX-003 從 10 日改 20 日回看的成功經驗（Sharpe 0.08→0.39）。
20 日回看捕捉更顯著的價格高點，進場時回檔深度更具意義。

Based on SIVR-005, extends pullback lookback from 10 to 20 days.
Inspired by COPX-003's success with 20-day lookback.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVRDivergencePullbackWRConfig(ExperimentConfig):
    """SIVR 20日回檔範圍 + Williams %R 參數"""

    # 進場指標
    pullback_lookback: int = 20  # 20 日回看（vs SIVR-005 的 10 日）
    pullback_threshold: float = -0.08  # 回檔 ≥8%（20日回看需更深回檔過濾噪音）
    pullback_cap: float = -0.15  # 回檔 ≤15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> SIVRDivergencePullbackWRConfig:
    return SIVRDivergencePullbackWRConfig(
        name="sivr_007_divergence_pullback_wr",
        experiment_id="SIVR-007",
        display_name="SIVR 20-Day Pullback + Williams %R Mean Reversion",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.035,  # -3.5%
        holding_days=15,  # 15 天
    )
