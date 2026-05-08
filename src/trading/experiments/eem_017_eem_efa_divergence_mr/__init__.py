"""EEM EEM-EFA Cross-Asset Divergence Filter on Vol-Transition MR (EEM-017)"""

from trading.experiments import register
from trading.experiments.eem_017_eem_efa_divergence_mr.strategy import EEM017Strategy

register("eem_017_eem_efa_divergence_mr")(EEM017Strategy)
