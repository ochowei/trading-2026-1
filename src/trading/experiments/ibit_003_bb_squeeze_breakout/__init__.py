"""IBIT BB Squeeze Breakout (IBIT-003)"""

from trading.experiments import register
from trading.experiments.ibit_003_bb_squeeze_breakout.strategy import (
    IBITBBSqueezeBreakoutStrategy,
)

register("ibit_003_bb_squeeze_breakout")(IBITBBSqueezeBreakoutStrategy)
