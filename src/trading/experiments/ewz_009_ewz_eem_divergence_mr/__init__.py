"""EWZ-009: EWZ-EEM Divergence-Gated Vol-Transition MR"""

from trading.experiments import register
from trading.experiments.ewz_009_ewz_eem_divergence_mr.strategy import EWZ009Strategy

register("ewz_009_ewz_eem_divergence_mr")(EWZ009Strategy)
