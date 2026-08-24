"""TLT TLT-SPY Cross-Asset Divergence Regime-Gated MR (TLT-014)"""

from trading.experiments import register
from trading.experiments.tlt_014_tlt_spy_divergence_mr.strategy import (
    TLT014TltSpyDivergenceMRStrategy,
)

register("tlt_014_tlt_spy_divergence_mr")(TLT014TltSpyDivergenceMRStrategy)
