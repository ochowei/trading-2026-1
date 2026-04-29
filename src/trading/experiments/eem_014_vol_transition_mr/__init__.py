"""EEM Post-Capitulation Vol-Transition MR (EEM-014)"""

from trading.experiments import register
from trading.experiments.eem_014_vol_transition_mr.strategy import EEM014Strategy

register("eem_014_vol_transition_mr")(EEM014Strategy)
