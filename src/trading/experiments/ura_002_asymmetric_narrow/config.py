"""
URA-002: 非對稱出場均值回歸
(URA Asymmetric Exit Mean Reversion)

基於 URA-001（回檔 10-20% + WR(10) ≤ -80）的進場條件，
將對稱出場 TP +6.0% / SL -6.0% 改為非對稱 TP +6.0% / SL -5.5%。
SL 收窄 0.5% 降低每筆虧損幅度，同時保留所有原始訊號與 WR 62.5%。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URAAsymmetricNarrowConfig(ExperimentConfig):
    """URA 非對稱出場 + 回檔範圍收窄參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 10


def create_default_config() -> URAAsymmetricNarrowConfig:
    return URAAsymmetricNarrowConfig(
        name="ura_002_asymmetric_narrow",
        experiment_id="URA-002",
        display_name="URA Asymmetric Exit + Narrow Pullback",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.055,  # -5.5%（非對稱：SL 收窄 0.5%）
        holding_days=20,  # 20 天
    )
