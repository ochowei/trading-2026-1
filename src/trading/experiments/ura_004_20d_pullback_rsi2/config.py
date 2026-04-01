"""
URA-004: 回檔 + RSI(2) + 2日急跌 均值回歸
(URA Pullback + RSI(2) + 2-Day Decline Mean Reversion)

基於 URA-003 進場架構（回檔 10-20% + RSI(2) < 15），
加入 2 日跌幅 ≤ -3% 作為近期恐慌確認，過濾緩慢漂移的假訊號。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA20dPullbackRSI2Config(ExperimentConfig):
    """URA 回檔 + RSI(2) + 2日急跌參數"""

    # 進場指標
    pullback_lookback: int = 10  # 10日回看（同 URA-003）
    pullback_threshold: float = -0.10  # 回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    two_day_decline: float = -0.03  # 2日跌幅 ≤ -3%
    cooldown_days: int = 10


def create_default_config() -> URA20dPullbackRSI2Config:
    return URA20dPullbackRSI2Config(
        name="ura_004_20d_pullback_rsi2",
        experiment_id="URA-004",
        display_name="URA Pullback + RSI(2) + 2-Day Decline",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%
        stop_loss=-0.055,  # -5.5%
        holding_days=20,
    )
