"""SIVR–USD Cross-Asset Divergence Regime-Gated MR (SIVR-020)"""

from trading.experiments import register
from trading.experiments.sivr_020_usd_regime_mr.strategy import SIVR020Strategy

register("sivr_020_usd_regime_mr")(SIVR020Strategy)
