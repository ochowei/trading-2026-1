"""NVDA Multi-Week Regime-Aware Relative Strength Momentum Pullback (NVDA-015)"""

from trading.experiments import register
from trading.experiments.nvda_015_regime_rs.strategy import (
    NVDA015RegimeRSStrategy,
)

register("nvda_015_regime_rs")(NVDA015RegimeRSStrategy)
