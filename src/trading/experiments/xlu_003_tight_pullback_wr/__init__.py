"""XLU Tight Pullback + Williams %R + Reversal Candle (XLU-003)"""

from trading.experiments import register
from trading.experiments.xlu_003_tight_pullback_wr.strategy import (
    XLUTightPullbackStrategy,
)

register("xlu_003_tight_pullback_wr")(XLUTightPullbackStrategy)
