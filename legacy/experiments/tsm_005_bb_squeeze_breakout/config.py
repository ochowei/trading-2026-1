"""
TSM-005: Bollinger Band Squeeze Breakout 配置

Hypothesis: TSM is a momentum-driven semiconductor stock (like NVDA/TSLA).
Breakout after volatility compression should capture explosive gains.
Based on NVDA-003 success (Sharpe 0.40/0.47), adapted for TSM daily vol ~2.1%.

Result: BB Squeeze Breakout FAILED on TSM (3 attempts, all Part B negative).
Att1 (TP+7%/SL-6%/25th pct/15d): Part A 0.38/Part B -0.42 (SL too tight).
Att2 (TP+8%/SL-7%/25th pct/15d): Part A 0.37/Part B -0.16 (best, still negative).
Att3 (TP+8%/SL-8%/20th pct/20d): Part A 0.14/Part B -0.18 (tighter squeeze worsened).
Final config uses Att2 parameters (best of 3 attempts).
TSM 2024-2025 has too many false breakouts from AI hype/geopolitical reversals.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMBBSqueezeConfig(ExperimentConfig):
    """TSM BB Squeeze Breakout strategy parameters"""

    # Bollinger Band parameters
    bb_period: int = 20
    bb_std: float = 2.0

    # Squeeze detection
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5

    # Trend confirmation
    sma_trend_period: int = 50

    # Cooldown
    cooldown_days: int = 15


def create_default_config() -> TSMBBSqueezeConfig:
    """Create default configuration"""
    return TSMBBSqueezeConfig(
        name="tsm_005_bb_squeeze_breakout",
        experiment_id="TSM-005",
        display_name="TSM BB Squeeze Breakout",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
