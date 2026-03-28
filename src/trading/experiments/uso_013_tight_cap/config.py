"""
USO 緊密回檔上限 + RSI(2) + 2日急跌配置 (USO-013)

假設：將回檔上限從 13% 收緊至 12%，過濾更多接近崩盤的邊際訊號。
12-13% 回檔區間的訊號以停損為主，移除後可降低 MDD 並提升風險調整後報酬。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOTightCapConfig(ExperimentConfig):
    """USO 緊密回檔上限 + RSI(2) + 2日急跌參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_max: float = -0.12  # 回檔 ≤ 12%（USO-012 為 13%）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%
    cooldown_days: int = 10


def create_default_config() -> USOTightCapConfig:
    return USOTightCapConfig(
        name="uso_013_tight_cap",
        experiment_id="USO-013",
        display_name="USO Tight Cap Pullback + RSI(2) + 2-Day Drop",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.0325,
        holding_days=10,
    )
