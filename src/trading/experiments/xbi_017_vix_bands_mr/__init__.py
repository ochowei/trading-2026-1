"""XBI VIX Implied-Vol Regime Bands Filter Pullback MR (XBI-017)"""

from trading.experiments import register
from trading.experiments.xbi_017_vix_bands_mr.strategy import (
    XBI017VixBandsMRStrategy,
)

register("xbi_017_vix_bands_mr")(XBI017VixBandsMRStrategy)
