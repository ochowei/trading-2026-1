"""TSM Momentum Pullback (TSM-006)"""

from trading.experiments import register
from trading.experiments.tsm_006_momentum_pullback.strategy import (
    TSMMomentumPullbackStrategy,
)

register("tsm_006_momentum_pullback")(TSMMomentumPullbackStrategy)
