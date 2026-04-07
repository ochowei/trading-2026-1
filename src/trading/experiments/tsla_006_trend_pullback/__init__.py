"""TSLA Trend Pullback Entry (TSLA-006)"""

from trading.experiments import register
from trading.experiments.tsla_006_trend_pullback.strategy import (
    TSLATrendPullbackStrategy,
)

register("tsla_006_trend_pullback")(TSLATrendPullbackStrategy)
