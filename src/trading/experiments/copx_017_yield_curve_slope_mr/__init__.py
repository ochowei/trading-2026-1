"""COPX Yield-Curve-Slope Industrial-Demand-Regime-Gated MR (COPX-017)"""

from trading.experiments import register
from trading.experiments.copx_017_yield_curve_slope_mr.strategy import (
    COPX017YieldCurveSlopeMRStrategy,
)

register("copx_017_yield_curve_slope_mr")(COPX017YieldCurveSlopeMRStrategy)
