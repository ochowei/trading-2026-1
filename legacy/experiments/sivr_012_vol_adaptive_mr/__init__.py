"""SIVR Volatility-Adaptive Mean Reversion (SIVR-012)"""

from trading.experiments import register
from trading.experiments.sivr_012_vol_adaptive_mr.strategy import (
    SIVRVolAdaptiveMRStrategy,
)

register("sivr_012_vol_adaptive_mr")(SIVRVolAdaptiveMRStrategy)
