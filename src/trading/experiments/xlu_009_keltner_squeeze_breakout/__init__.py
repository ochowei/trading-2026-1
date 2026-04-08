"""XLU Keltner Channel Squeeze Breakout (XLU-009)"""

from trading.experiments import register
from trading.experiments.xlu_009_keltner_squeeze_breakout.strategy import (
    XLU009KeltnerSqueezeStrategy,
)

register("xlu_009_keltner_squeeze_breakout")(XLU009KeltnerSqueezeStrategy)
