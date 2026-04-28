"""FCX Multi-Week Regime-Aware BB Squeeze Breakout (FCX-013)"""

from trading.experiments import register
from trading.experiments.fcx_013_regime_breakout.strategy import (
    FCX013RegimeBreakoutStrategy,
)

register("fcx_013_regime_breakout")(FCX013RegimeBreakoutStrategy)
