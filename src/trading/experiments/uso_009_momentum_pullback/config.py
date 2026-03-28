"""
USO 回檔 + RSI(2) + 2日急跌配置 (USO-009)

假設：在 USO-007 基礎上加入 2 日報酬 ≤ -2.5% 條件，
確保回檔是近期急跌（V 型反轉潛力高），過濾緩慢磨底的弱訊號。
靈感來自 SPY-004（RSI(2) + 2日跌幅）的成功經驗。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USOMomentumPullbackConfig(ExperimentConfig):
    """USO 回檔 + RSI(2) + 2日急跌參數"""

    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 回檔 ≥6%（同 USO-007）
    rsi_period: int = 2
    rsi_threshold: float = 15.0  # RSI(2) < 15
    drop_2d_threshold: float = -0.025  # 2日報酬 ≤ -2.5%
    cooldown_days: int = 10


def create_default_config() -> USOMomentumPullbackConfig:
    return USOMomentumPullbackConfig(
        name="uso_009_momentum_pullback",
        experiment_id="USO-009",
        display_name="USO Pullback + RSI(2) + 2-Day Drop",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.03,
        stop_loss=-0.0325,
        holding_days=10,
    )
