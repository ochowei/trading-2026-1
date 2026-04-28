"""FCX RSI Bullish Hook Divergence + Pullback+WR Mean Reversion (FCX-009)"""

from trading.experiments import register
from trading.experiments.fcx_009_rsi_divergence_mr.strategy import (
    FCXRSIDivergenceMRStrategy,
)

register("fcx_009_rsi_divergence_mr")(FCXRSIDivergenceMRStrategy)
