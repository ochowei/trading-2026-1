"""USO Bollinger Band Squeeze Breakout (USO-021)"""

from trading.experiments import register
from trading.experiments.uso_021_bb_squeeze_breakout.strategy import (
    USOBBSqueezeBreakoutStrategy,
)

register("uso_021_bb_squeeze_breakout")(USOBBSqueezeBreakoutStrategy)
