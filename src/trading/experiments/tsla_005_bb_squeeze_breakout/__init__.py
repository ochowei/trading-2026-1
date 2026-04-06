"""TSLA Bollinger Band Squeeze Breakout (TSLA-005)"""

from trading.experiments import register
from trading.experiments.tsla_005_bb_squeeze_breakout.strategy import (
    TSLABBSqueezeBreakoutStrategy,
)

register("tsla_005_bb_squeeze_breakout")(TSLABBSqueezeBreakoutStrategy)
