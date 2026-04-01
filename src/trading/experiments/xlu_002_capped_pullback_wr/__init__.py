"""XLU Capped Pullback + Williams %R + Reversal Candle (XLU-002)"""

from trading.experiments import register
from trading.experiments.xlu_002_capped_pullback_wr.strategy import (
    XLURsi2ReversalStrategy,
)

register("xlu_002_capped_pullback_wr")(XLURsi2ReversalStrategy)
