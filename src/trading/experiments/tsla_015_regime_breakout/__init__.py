"""TSLA Multi-Week Regime-Aware BB Squeeze Breakout (TSLA-015)"""

from trading.experiments import register
from trading.experiments.tsla_015_regime_breakout.strategy import (
    TSLA015RegimeBreakoutStrategy,
)

register("tsla_015_regime_breakout")(TSLA015RegimeBreakoutStrategy)
