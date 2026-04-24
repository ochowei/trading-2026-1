"""TLT Dynamic BB-Width Percentile Regime MR (TLT-011)"""

from trading.experiments import register
from trading.experiments.tlt_011_dynamic_regime_mr.strategy import (
    TLT011DynamicRegimeMRStrategy,
)

register("tlt_011_dynamic_regime_mr")(TLT011DynamicRegimeMRStrategy)
