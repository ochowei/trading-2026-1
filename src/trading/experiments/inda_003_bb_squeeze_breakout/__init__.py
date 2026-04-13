"""INDA BB Squeeze Breakout (INDA-003)"""

from trading.experiments import register
from trading.experiments.inda_003_bb_squeeze_breakout.strategy import INDA003Strategy

register("inda_003_bb_squeeze_breakout")(INDA003Strategy)
