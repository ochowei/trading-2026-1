"""IWM Momentum Breakout Pullback Continuation (IWM-014)"""

from trading.experiments import register
from trading.experiments.iwm_014_momentum_pullback.strategy import (
    IWM014MomentumPullbackStrategy,
)

register("iwm_014_momentum_pullback")(IWM014MomentumPullbackStrategy)
