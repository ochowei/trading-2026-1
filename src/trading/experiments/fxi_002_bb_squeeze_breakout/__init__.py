"""FXI BB Squeeze Breakout (FXI-002)"""

from trading.experiments import register
from trading.experiments.fxi_002_bb_squeeze_breakout.strategy import FXI002Strategy

register("fxi_002_bb_squeeze_breakout")(FXI002Strategy)
