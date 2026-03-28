"""
USO 深回檔 + RSI(2) + 2日急跌配置 (USO-010)

假設：將回檔門檻從 6% 提高至 7%，適度收緊進場過濾淺回檔訊號，
同時不過度減少訊號數量。其餘參數同 USO-009。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USODeepPullbackConfig(ExperimentConfig):
    """USO 深回檔 + RSI(2) + 2日急跌參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%（較 USO-009 適度收緊）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%
    cooldown_days: int = 10


def create_default_config() -> USODeepPullbackConfig:
    return USODeepPullbackConfig(
        name="uso_010_deep_pullback",
        experiment_id="USO-010",
        display_name="USO Deep Pullback + RSI(2) + 2-Day Drop",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.0325,
        holding_days=10,
    )
