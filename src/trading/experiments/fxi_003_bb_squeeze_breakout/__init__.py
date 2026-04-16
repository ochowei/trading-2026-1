"""FXI BB Squeeze Breakout (FXI-003)"""

from trading.experiments import register
from trading.experiments.fxi_003_bb_squeeze_breakout.strategy import FXI003Strategy

register("fxi_003_bb_squeeze_breakout")(FXI003Strategy)
