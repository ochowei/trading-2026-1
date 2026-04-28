"""EWT Post-Capitulation Vol-Transition MR (EWT-009)"""

from trading.experiments import register
from trading.experiments.ewt_009_vol_transition_mr.strategy import EWT009Strategy

register("ewt_009_vol_transition_mr")(EWT009Strategy)
