"""EEM BB Squeeze Breakout (EEM-005)"""

from trading.experiments import register
from trading.experiments.eem_005_bb_squeeze_breakout.strategy import EEM005Strategy

register("eem_005_bb_squeeze_breakout")(EEM005Strategy)
