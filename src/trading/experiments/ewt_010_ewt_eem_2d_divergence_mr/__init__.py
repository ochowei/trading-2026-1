"""EWT-010: EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR"""

from trading.experiments import register
from trading.experiments.ewt_010_ewt_eem_2d_divergence_mr.strategy import (
    EWT010Strategy,
)

register("ewt_010_ewt_eem_2d_divergence_mr")(EWT010Strategy)
