"""TQQQ BB Squeeze Breakout (TQQQ-native) (TQQQ-028)"""

from trading.experiments import register
from trading.experiments.tqqq_028_bb_squeeze_breakout.strategy import (
    TQQQ028BBSqueezeStrategy,
)

register("tqqq_028_bb_squeeze_breakout")(TQQQ028BBSqueezeStrategy)
