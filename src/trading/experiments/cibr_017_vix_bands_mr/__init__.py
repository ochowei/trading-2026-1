"""CIBR ^VIX Implied-Vol Regime BANDS Filter MR (CIBR-017)"""

from trading.experiments import register
from trading.experiments.cibr_017_vix_bands_mr.strategy import (
    CIBR017VixBandsMRStrategy,
)

register("cibr_017_vix_bands_mr")(CIBR017VixBandsMRStrategy)
