"""EWT BB Squeeze Breakout (EWT-003)"""

from trading.experiments import register
from trading.experiments.ewt_003_bb_squeeze_breakout.strategy import EWT003Strategy

register("ewt_003_bb_squeeze_breakout")(EWT003Strategy)
