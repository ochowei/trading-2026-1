"""COPX Multi-Week Regime-Aware BB Squeeze Breakout (COPX-011)"""

from trading.experiments import register
from trading.experiments.copx_011_regime_breakout.strategy import (
    COPX011RegimeBreakoutStrategy,
)

register("copx_011_regime_breakout")(COPX011RegimeBreakoutStrategy)
