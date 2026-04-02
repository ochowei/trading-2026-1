"""TSM Bollinger Band Squeeze Breakout (TSM-005)"""

from trading.experiments import register
from trading.experiments.tsm_005_bb_squeeze_breakout.strategy import (
    TSMBBSqueezeBreakoutStrategy,
)

register("tsm_005_bb_squeeze_breakout")(TSMBBSqueezeBreakoutStrategy)
