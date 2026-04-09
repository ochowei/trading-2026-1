"""XLU Volatility-Adaptive Mean Reversion (XLU-011)"""

from trading.experiments import register
from trading.experiments.xlu_011_vol_adaptive_mr.strategy import (
    XLUVolAdaptiveMRStrategy,
)

register("xlu_011_vol_adaptive_mr")(XLUVolAdaptiveMRStrategy)
