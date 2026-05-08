"""TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback (TSM-014)"""

from trading.experiments import register
from trading.experiments.tsm_014_qqq_divergence_band.strategy import (
    TSM014QQQDivergenceBandStrategy,
)

register("tsm_014_qqq_divergence_band")(TSM014QQQDivergenceBandStrategy)
