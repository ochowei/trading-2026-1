"""TLT Yield-Velocity-Gated Mean Reversion (TLT-009)"""

from trading.experiments import register
from trading.experiments.tlt_009_yield_velocity_mr.strategy import (
    TLT009YieldVelocityMRStrategy,
)

register("tlt_009_yield_velocity_mr")(TLT009YieldVelocityMRStrategy)
