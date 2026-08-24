"""XLU Momentum Pullback (XLU-007)"""

from trading.experiments import register
from trading.experiments.xlu_007_momentum_pullback.strategy import (
    XLU007MomentumPullbackStrategy,
)

register("xlu_007_momentum_pullback")(XLU007MomentumPullbackStrategy)
