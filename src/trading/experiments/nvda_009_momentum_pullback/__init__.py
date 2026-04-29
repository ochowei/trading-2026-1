"""NVDA Momentum Breakout Pullback Continuation (NVDA-009)"""

from trading.experiments import register
from trading.experiments.nvda_009_momentum_pullback.strategy import (
    NVDA009MomentumPullbackStrategy,
)

register("nvda_009_momentum_pullback")(NVDA009MomentumPullbackStrategy)
