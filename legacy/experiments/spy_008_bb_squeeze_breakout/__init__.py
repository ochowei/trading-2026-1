"""SPY Bollinger Band Squeeze Breakout (SPY-008)"""

from trading.experiments import register
from trading.experiments.spy_008_bb_squeeze_breakout.strategy import (
    SPYBBSqueezeBreakoutStrategy,
)

register("spy_008_bb_squeeze_breakout")(SPYBBSqueezeBreakoutStrategy)
