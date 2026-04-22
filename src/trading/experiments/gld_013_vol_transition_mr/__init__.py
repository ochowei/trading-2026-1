"""GLD Post-Capitulation Vol-Transition MR (GLD-013)"""

from trading.experiments import register
from trading.experiments.gld_013_vol_transition_mr.strategy import GLD013Strategy

register("gld_013_vol_transition_mr")(GLD013Strategy)
