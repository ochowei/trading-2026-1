"""XBI RSI Bullish Divergence + Pullback+WR+ClosePos Mean Reversion (XBI-011)"""

from trading.experiments import register
from trading.experiments.xbi_011_rsi_divergence_mr.strategy import (
    XBI011Strategy,
)

register("xbi_011_rsi_divergence_mr")(XBI011Strategy)
