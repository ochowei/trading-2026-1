"""TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback (TSM-013)"""

from trading.experiments import register
from trading.experiments.tsm_013_qqq_divergence_rs.strategy import (
    TSM013QQQDivergenceRSStrategy,
)

register("tsm_013_qqq_divergence_rs")(TSM013QQQDivergenceRSStrategy)
