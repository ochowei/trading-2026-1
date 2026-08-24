"""TSLA ^VIX BANDS Regime Gate on TSLA-017 Att3 BB Squeeze Breakout (TSLA-019)"""

from trading.experiments import register
from trading.experiments.tsla_019_vix_bands_breakout.strategy import (
    TSLA019VixBandsBreakoutStrategy,
)

register("tsla_019_vix_bands_breakout")(TSLA019VixBandsBreakoutStrategy)
