"""
URA-003: 回檔 + RSI(2) 均值回歸
(URA Pullback + RSI(2) Mean Reversion)

基於 URA-002 進場架構，以 RSI(2) < 15 替代 WR(10) ≤ -80，
短週期超賣指標更精準捕捉短期動量耗竭。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URAPullbackRSI2Config(ExperimentConfig):
    """URA 回檔 + RSI(2) 參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    cooldown_days: int = 10


def create_default_config() -> URAPullbackRSI2Config:
    return URAPullbackRSI2Config(
        name="ura_003_pullback_rsi2",
        experiment_id="URA-003",
        display_name="URA Pullback + RSI(2)",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.055,  # -5.5%
        holding_days=20,
    )
