"""SPY-007: Trend Pullback to SMA(50)"""

from trading.experiments import register
from trading.experiments.spy_007_trend_pullback.strategy import (
    SPY007TrendPullbackStrategy,
)

register("spy_007_trend_pullback")(SPY007TrendPullbackStrategy)
