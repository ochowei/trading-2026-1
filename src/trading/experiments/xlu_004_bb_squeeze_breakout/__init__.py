"""XLU Bollinger Band Squeeze Breakout (XLU-004)"""

from trading.experiments import register
from trading.experiments.xlu_004_bb_squeeze_breakout.strategy import (
    XLU004BBSqueezeStrategy,
)

register("xlu_004_bb_squeeze_breakout")(XLU004BBSqueezeStrategy)
