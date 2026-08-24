"""EWZ Post-Capitulation Vol-Transition MR (EWZ-007)"""

from trading.experiments import register
from trading.experiments.ewz_007_vol_transition_mr.strategy import EWZ007Strategy

register("ewz_007_vol_transition_mr")(EWZ007Strategy)
