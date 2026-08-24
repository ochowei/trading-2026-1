"""EWZ BB Squeeze Breakout (EWZ-003)"""

from trading.experiments import register
from trading.experiments.ewz_003_bb_squeeze_breakout.strategy import EWZ003Strategy

register("ewz_003_bb_squeeze_breakout")(EWZ003Strategy)
