"""GLD–USD Cross-Asset Divergence Regime-Gated MR (GLD-016)"""

from trading.experiments import register
from trading.experiments.gld_016_usd_regime_mr.strategy import (
    GLD016UsdRegimeMRStrategy,
)

register("gld_016_usd_regime_mr")(GLD016UsdRegimeMRStrategy)
