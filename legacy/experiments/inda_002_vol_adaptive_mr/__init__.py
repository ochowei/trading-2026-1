"""INDA Volatility-Adaptive Mean Reversion (INDA-002)"""

from trading.experiments import register
from trading.experiments.inda_002_vol_adaptive_mr.strategy import (
    INDAVolAdaptiveMRStrategy,
)

register("inda_002_vol_adaptive_mr")(INDAVolAdaptiveMRStrategy)
