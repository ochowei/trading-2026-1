"""GLD–USD Cross-Asset Divergence Regime-Gated MR (GLD-017)"""

from trading.experiments import register
from trading.experiments.gld_017_usd_regime_mr.strategy import (
    GLD017UsdRegimeMRStrategy,
)

register("gld_017_usd_regime_mr")(GLD017UsdRegimeMRStrategy)
