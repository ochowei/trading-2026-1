"""EWT EWT–EEM Cross-Asset Divergence Regime-Gated MR (EWT-012)"""

from trading.experiments import register
from trading.experiments.ewt_012_eem_divergence_regime_mr.strategy import (
    EWT012EemDivergenceRegimeMRStrategy,
)

register("ewt_012_eem_divergence_regime_mr")(EWT012EemDivergenceRegimeMRStrategy)
