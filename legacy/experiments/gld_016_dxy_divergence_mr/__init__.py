"""GLD DXY USD Cross-Asset Divergence Filter on GVZ-Gated MR (GLD-016)"""

from trading.experiments import register
from trading.experiments.gld_016_dxy_divergence_mr.strategy import (
    GLD016DxyDivergenceMRStrategy,
)

register("gld_016_dxy_divergence_mr")(GLD016DxyDivergenceMRStrategy)
