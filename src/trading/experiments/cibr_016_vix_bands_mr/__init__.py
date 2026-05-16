"""CIBR ^VIX Implied-Vol Regime BANDS Filter MR (CIBR-016)"""

from trading.experiments import register
from trading.experiments.cibr_016_vix_bands_mr.strategy import (
    CIBR016VixBandsMRStrategy,
)

register("cibr_016_vix_bands_mr")(CIBR016VixBandsMRStrategy)
