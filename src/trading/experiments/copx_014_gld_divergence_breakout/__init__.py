"""COPX COPX-GLD Cross-Asset Divergence Regime-Gated BB Squeeze Breakout (COPX-014)"""

from trading.experiments import register
from trading.experiments.copx_014_gld_divergence_breakout.strategy import (
    COPX014GldDivergenceBreakoutStrategy,
)

register("copx_014_gld_divergence_breakout")(COPX014GldDivergenceBreakoutStrategy)
