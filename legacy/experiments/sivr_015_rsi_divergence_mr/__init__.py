"""SIVR RSI Bullish Divergence + Pullback+WR Mean Reversion (SIVR-015)"""

from trading.experiments import register
from trading.experiments.sivr_015_rsi_divergence_mr.strategy import (
    SIVRRSIDivergenceMRStrategy,
)

register("sivr_015_rsi_divergence_mr")(SIVRRSIDivergenceMRStrategy)
