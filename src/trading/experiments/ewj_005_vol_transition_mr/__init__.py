"""EWJ Post-Capitulation Vol-Transition MR (EWJ-005)"""

from trading.experiments import register
from trading.experiments.ewj_005_vol_transition_mr.strategy import EWJ005Strategy

register("ewj_005_vol_transition_mr")(EWJ005Strategy)
