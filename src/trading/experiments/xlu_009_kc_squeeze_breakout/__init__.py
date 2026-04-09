"""XLU Keltner Channel Squeeze Breakout (XLU-009)"""

from trading.experiments import register
from trading.experiments.xlu_009_kc_squeeze_breakout.strategy import (
    XLU009KCSqueezeStrategy,
)

register("xlu_009_kc_squeeze_breakout")(XLU009KCSqueezeStrategy)
