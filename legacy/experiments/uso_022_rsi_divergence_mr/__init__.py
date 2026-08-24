"""USO RSI(14) Bullish Hook Divergence + USO-013 框架 (USO-022)"""

from trading.experiments import register
from trading.experiments.uso_022_rsi_divergence_mr.strategy import (
    USORSIDivergenceMRStrategy,
)

register("uso_022_rsi_divergence_mr")(USORSIDivergenceMRStrategy)
