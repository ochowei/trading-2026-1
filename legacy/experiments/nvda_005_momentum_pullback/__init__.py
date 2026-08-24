"""NVDA Momentum Pullback (NVDA-005)"""

from trading.experiments import register
from trading.experiments.nvda_005_momentum_pullback.strategy import (
    NVDAMomentumPullbackStrategy,
)

register("nvda_005_momentum_pullback")(NVDAMomentumPullbackStrategy)
