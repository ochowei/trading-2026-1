"""IWM Bollinger Band Squeeze Breakout (IWM-006)"""

from trading.experiments import register
from trading.experiments.iwm_006_bb_squeeze_breakout.strategy import (
    IWM006BBSqueezeStrategy,
)

register("iwm_006_bb_squeeze_breakout")(IWM006BBSqueezeStrategy)
