"""TSM-AAPL Cross-Asset Divergence Regime-Gated RS Momentum Pullback (TSM-015)"""

from trading.experiments import register
from trading.experiments.tsm_015_aapl_divergence_rs.strategy import (
    TSM015AAPLDivergenceStrategy,
)

register("tsm_015_aapl_divergence_rs")(TSM015AAPLDivergenceStrategy)
