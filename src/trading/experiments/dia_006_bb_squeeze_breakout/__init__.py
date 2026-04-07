"""DIA Bollinger Band Squeeze Breakout (DIA-006)"""

from trading.experiments import register
from trading.experiments.dia_006_bb_squeeze_breakout.strategy import (
    DIA006BBSqueezeStrategy,
)

register("dia_006_bb_squeeze_breakout")(DIA006BBSqueezeStrategy)
