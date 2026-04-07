"""IWM Bollinger Band Squeeze Breakout Optimized (IWM-008)"""

from trading.experiments import register
from trading.experiments.iwm_008_bb_squeeze_optimized.strategy import (
    IWM008BBSqueezeStrategy,
)

register("iwm_008_bb_squeeze_optimized")(IWM008BBSqueezeStrategy)
