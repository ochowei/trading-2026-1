"""COPX Volatility-Acceleration-Bounded MR (COPX-012)"""

from trading.experiments import register
from trading.experiments.copx_012_atr_ceiling_mr.strategy import (
    COPX012Strategy,
)

register("copx_012_atr_ceiling_mr")(COPX012Strategy)
