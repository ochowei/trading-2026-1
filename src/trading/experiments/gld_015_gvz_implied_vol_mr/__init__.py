"""GLD GVZ Implied Volatility Forward-Looking Regime-Gated MR (GLD-015)"""

from trading.experiments import register
from trading.experiments.gld_015_gvz_implied_vol_mr.strategy import (
    GLD015GvzImpliedVolMRStrategy,
)

register("gld_015_gvz_implied_vol_mr")(GLD015GvzImpliedVolMRStrategy)
