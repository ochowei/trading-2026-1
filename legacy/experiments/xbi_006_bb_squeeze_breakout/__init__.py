"""XBI Bollinger Band Squeeze Breakout (XBI-006)"""

from trading.experiments import register
from trading.experiments.xbi_006_bb_squeeze_breakout.strategy import (
    XBI006BBSqueezeStrategy,
)

register("xbi_006_bb_squeeze_breakout")(XBI006BBSqueezeStrategy)
