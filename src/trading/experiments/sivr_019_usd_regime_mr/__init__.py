"""SIVR–USD Cross-Asset Divergence Regime-Gated MR (SIVR-019)"""

from trading.experiments import register
from trading.experiments.sivr_019_usd_regime_mr.strategy import SIVR019Strategy

register("sivr_019_usd_regime_mr")(SIVR019Strategy)
