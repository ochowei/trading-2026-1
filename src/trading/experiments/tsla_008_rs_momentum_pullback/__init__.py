"""TSLA BB Squeeze + Golden Cross (TSLA-008)"""

from trading.experiments import register
from trading.experiments.tsla_008_rs_momentum_pullback.strategy import (
    TSLARSMomentumPullbackStrategy,
)

register("tsla_008_rs_momentum_pullback")(TSLARSMomentumPullbackStrategy)
