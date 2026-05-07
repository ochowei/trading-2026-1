"""FCX VIX BANDS Filter on BB Squeeze Breakout (FCX-015)"""

from trading.experiments import register
from trading.experiments.fcx_015_vix_bands_breakout.strategy import (
    FCX015VixBandsBreakoutStrategy,
)

register("fcx_015_vix_bands_breakout")(FCX015VixBandsBreakoutStrategy)
