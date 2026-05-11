"""EEM-019: EEM-FXI Cross-Asset Divergence Filter on Vol-Transition MR"""

from trading.experiments import register
from trading.experiments.eem_019_eem_fxi_divergence_mr.strategy import EEM019Strategy

register("eem_019_eem_fxi_divergence_mr")(EEM019Strategy)
