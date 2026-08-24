"""URA BB Squeeze Breakout (URA-005)"""

from trading.experiments import register
from trading.experiments.ura_005_bb_squeeze_breakout.strategy import (
    URABBSqueezeBreakoutStrategy,
)

register("ura_005_bb_squeeze_breakout")(URABBSqueezeBreakoutStrategy)
