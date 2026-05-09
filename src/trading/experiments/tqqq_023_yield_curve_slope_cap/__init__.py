"""TQQQ Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy (TQQQ-023)"""

from trading.experiments import register
from trading.experiments.tqqq_023_yield_curve_slope_cap.strategy import (
    TQQQ023YieldCurveSlopeStrategy,
)

register("tqqq_023_yield_curve_slope_cap")(TQQQ023YieldCurveSlopeStrategy)
