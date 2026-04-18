"""COPX RSI Bullish Divergence + Pullback+WR+ATR Mean Reversion (COPX-009)"""

from trading.experiments import register
from trading.experiments.copx_009_rsi_divergence_mr.strategy import (
    COPX009Strategy,
)

register("copx_009_rsi_divergence_mr")(COPX009Strategy)
