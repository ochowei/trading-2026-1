"""EWT EWT–EEM Cross-Asset Divergence Regime-Gated MR (EWT-010)"""

from trading.experiments import register
from trading.experiments.ewt_010_eem_divergence_regime_mr.strategy import (
    EWT010EemDivergenceRegimeMRStrategy,
)

register("ewt_010_eem_divergence_regime_mr")(EWT010EemDivergenceRegimeMRStrategy)
