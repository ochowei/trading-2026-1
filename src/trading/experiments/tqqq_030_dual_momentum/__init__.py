"""TQQQ Dual-Horizon Momentum Continuation (TQQQ-native) (TQQQ-030)"""

from trading.experiments import register
from trading.experiments.tqqq_030_dual_momentum.strategy import (
    TQQQ030DualMomentumStrategy,
)

register("tqqq_030_dual_momentum")(TQQQ030DualMomentumStrategy)
