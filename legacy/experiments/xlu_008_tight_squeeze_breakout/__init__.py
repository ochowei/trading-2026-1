"""XLU Tight BB Squeeze Breakout (XLU-008)"""

from trading.experiments import register
from trading.experiments.xlu_008_tight_squeeze_breakout.strategy import (
    XLU008TightSqueezeStrategy,
)

register("xlu_008_tight_squeeze_breakout")(XLU008TightSqueezeStrategy)
