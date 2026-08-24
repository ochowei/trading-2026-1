"""TLT Bollinger Band Squeeze Breakout (TLT-004)"""

from trading.experiments import register
from trading.experiments.tlt_004_bb_squeeze_breakout.strategy import (
    TLTBBSqueezeBreakoutStrategy,
)

register("tlt_004_bb_squeeze_breakout")(TLTBBSqueezeBreakoutStrategy)
