"""GLD BB Squeeze Breakout (GLD-009)"""

from trading.experiments import register
from trading.experiments.gld_009_bb_squeeze_breakout.strategy import (
    GLDBBSqueezeBreakoutStrategy,
)

register("gld_009_bb_squeeze_breakout")(GLDBBSqueezeBreakoutStrategy)
