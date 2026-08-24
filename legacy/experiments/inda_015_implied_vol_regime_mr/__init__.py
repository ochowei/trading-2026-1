"""INDA Implied-Vol Regime-Gated MR (INDA-015)"""

from trading.experiments import register
from trading.experiments.inda_015_implied_vol_regime_mr.strategy import (
    INDA015Strategy,
)

register("inda_015_implied_vol_regime_mr")(INDA015Strategy)
