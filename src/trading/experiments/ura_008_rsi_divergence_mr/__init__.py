"""URA RSI Bullish Divergence + Pullback + RSI(2) + 2-Day Decline (URA-008)"""

from trading.experiments import register
from trading.experiments.ura_008_rsi_divergence_mr.strategy import (
    URARSIDivergenceMRStrategy,
)

register("ura_008_rsi_divergence_mr")(URARSIDivergenceMRStrategy)
