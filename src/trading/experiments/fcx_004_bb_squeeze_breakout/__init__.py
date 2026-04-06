"""FCX Bollinger Band Squeeze Breakout (FCX-004)"""

from trading.experiments import register
from trading.experiments.fcx_004_bb_squeeze_breakout.strategy import (
    FCXBBSqueezeBreakoutStrategy,
)

register("fcx_004_bb_squeeze_breakout")(FCXBBSqueezeBreakoutStrategy)
