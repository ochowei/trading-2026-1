"""FCX Momentum Pullback (FCX-005)"""

from trading.experiments import register
from trading.experiments.fcx_005_momentum_pullback.strategy import (
    FCXMomentumPullbackStrategy,
)

register("fcx_005_momentum_pullback")(FCXMomentumPullbackStrategy)
