"""TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback (TSM-020)"""

from trading.experiments import register
from trading.experiments.tsm_020_soxx_divergence_rs.strategy import (
    TSM020SOXXDivergenceRSStrategy,
)

register("tsm_020_soxx_divergence_rs")(TSM020SOXXDivergenceRSStrategy)
