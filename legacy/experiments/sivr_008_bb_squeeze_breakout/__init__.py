"""SIVR Bollinger Band Squeeze Breakout (SIVR-008)"""

from trading.experiments import register
from trading.experiments.sivr_008_bb_squeeze_breakout.strategy import (
    SIVRBBSqueezeBreakoutStrategy,
)

register("sivr_008_bb_squeeze_breakout")(SIVRBBSqueezeBreakoutStrategy)
