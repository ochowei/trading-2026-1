"""SPY-010: Trend Pullback Family Baseline"""

from trading.experiments import register
from trading.experiments.spy_010_trend_pullback_baseline.strategy import (
    SPY010TrendPullbackBaselineStrategy,
)

register("spy_010_trend_pullback_baseline")(SPY010TrendPullbackBaselineStrategy)
