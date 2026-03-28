"""
USO 回檔範圍過濾 + RSI(2) + 2日急跌配置 (USO-012)

假設：在 USO-010 基礎上加入回檔上限 13%，過濾極端崩盤訊號。
正常均值回歸在 7-13% 回檔範圍有效，超過 13% 通常為市場崩盤，
賣壓過強無法在 +3% TP 內回歸。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOCappedPullbackConfig(ExperimentConfig):
    """USO 回檔範圍過濾 + RSI(2) + 2日急跌參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_max: float = -0.13  # 回檔 ≤ 13%（過濾極端崩盤）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%
    cooldown_days: int = 10


def create_default_config() -> USOCappedPullbackConfig:
    return USOCappedPullbackConfig(
        name="uso_012_capped_pullback",
        experiment_id="USO-012",
        display_name="USO Capped Pullback + RSI(2) + 2-Day Drop",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.0325,
        holding_days=10,
    )
