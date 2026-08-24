"""VOO Momentum Breakout Pullback Continuation (VOO-004)"""

from trading.experiments import register
from trading.experiments.voo_004_momentum_pullback.strategy import (
    VOO004MomentumPullbackStrategy,
)

register("voo_004_momentum_pullback")(VOO004MomentumPullbackStrategy)
