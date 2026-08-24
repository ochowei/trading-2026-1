"""COPX VIX BANDS Filter on BB Squeeze Breakout (COPX-015)"""

from trading.experiments import register
from trading.experiments.copx_015_vix_bands_breakout.strategy import (
    COPX015VixBandsBreakoutStrategy,
)

register("copx_015_vix_bands_breakout")(COPX015VixBandsBreakoutStrategy)
