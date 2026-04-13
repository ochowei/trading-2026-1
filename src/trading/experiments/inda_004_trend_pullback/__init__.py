"""INDA Trend Pullback (INDA-004)"""

from trading.experiments import register
from trading.experiments.inda_004_trend_pullback.strategy import (
    INDATrendPullbackStrategy,
)

register("inda_004_trend_pullback")(INDATrendPullbackStrategy)
