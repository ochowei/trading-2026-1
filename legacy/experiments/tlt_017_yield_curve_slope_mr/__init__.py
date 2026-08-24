"""TLT Yield-Curve-Slope Inflation-Regime-Gated MR (TLT-017)"""

from trading.experiments import register
from trading.experiments.tlt_017_yield_curve_slope_mr.strategy import (
    TLT017YieldCurveSlopeMRStrategy,
)

register("tlt_017_yield_curve_slope_mr")(TLT017YieldCurveSlopeMRStrategy)
