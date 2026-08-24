"""XBI Momentum Pullback (XBI-007)"""

from trading.experiments import register
from trading.experiments.xbi_007_momentum_pullback.strategy import (
    XBIMomentumPullbackStrategy,
)

register("xbi_007_momentum_pullback")(XBIMomentumPullbackStrategy)
