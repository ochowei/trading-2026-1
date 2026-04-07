"""XLU Trend Pullback (XLU-005)"""

from trading.experiments import register
from trading.experiments.xlu_005_trend_pullback.strategy import (
    XLU005TrendPullbackStrategy,
)

register("xlu_005_trend_pullback")(XLU005TrendPullbackStrategy)
