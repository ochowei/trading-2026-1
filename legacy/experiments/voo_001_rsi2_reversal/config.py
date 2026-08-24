"""
VOO-001: RSI(2) 極端超賣均值回歸
(VOO RSI(2) Extreme Oversold Mean Reversion)

移植自 SPY-004，VOO 與 SPY 追蹤相同的 S&P 500 指數，
日波動率相同（~1.0-1.2%），參數完全沿用。

Ported from SPY-004. VOO and SPY track the same S&P 500 index
with identical daily volatility (~1.0-1.2%), so all parameters are unchanged.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VOORsi2Config(ExperimentConfig):
    """VOO RSI(2) 極端超賣均值回歸參數"""

    # RSI(2) 參數
    rsi_period: int = 2
    rsi_threshold: float = 10.0  # RSI(2) < 10（極端超賣）

    # 2 日累計跌幅過濾
    decline_lookback: int = 2
    decline_threshold: float = -0.015  # 2 日跌幅 >= 1.5%

    # 收盤位置過濾（反轉確認）
    close_position_threshold: float = 0.4  # (Close-Low)/(High-Low) >= 40%

    # 冷卻期
    cooldown_days: int = 5


def create_default_config() -> VOORsi2Config:
    return VOORsi2Config(
        name="voo_001_rsi2_reversal",
        experiment_id="VOO-001",
        display_name="VOO RSI(2) Extreme Oversold Reversal",
        tickers=["VOO"],
        data_start="2010-10-01",
        profit_target=0.025,  # +2.5%
        stop_loss=-0.025,  # -2.5%（與 TP 對稱）
        holding_days=15,  # 15 天
    )
