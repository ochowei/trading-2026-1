"""USO Multi-Week Regime-Aware BB Squeeze Breakout (USO-024)"""

from trading.experiments import register
from trading.experiments.uso_024_regime_breakout.strategy import (
    USO024RegimeBreakoutStrategy,
)

register("uso_024_regime_breakout")(USO024RegimeBreakoutStrategy)
