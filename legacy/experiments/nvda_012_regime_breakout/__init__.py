"""NVDA Multi-Week Regime-Aware BB Squeeze Breakout (NVDA-012)"""

from trading.experiments import register
from trading.experiments.nvda_012_regime_breakout.strategy import (
    NVDA012RegimeBreakoutStrategy,
)

register("nvda_012_regime_breakout")(NVDA012RegimeBreakoutStrategy)
