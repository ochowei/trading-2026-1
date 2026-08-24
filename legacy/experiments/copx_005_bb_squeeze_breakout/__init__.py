"""COPX Bollinger Band Squeeze Breakout (COPX-005)"""

from trading.experiments import register
from trading.experiments.copx_005_bb_squeeze_breakout.strategy import (
    COPXBBSqueezeBreakoutStrategy,
)

register("copx_005_bb_squeeze_breakout")(COPXBBSqueezeBreakoutStrategy)
