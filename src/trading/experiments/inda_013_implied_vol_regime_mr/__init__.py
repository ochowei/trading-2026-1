"""INDA Implied-Vol Regime-Gated MR (INDA-013)"""

from trading.experiments import register
from trading.experiments.inda_013_implied_vol_regime_mr.strategy import (
    INDA013Strategy,
)

register("inda_013_implied_vol_regime_mr")(INDA013Strategy)
