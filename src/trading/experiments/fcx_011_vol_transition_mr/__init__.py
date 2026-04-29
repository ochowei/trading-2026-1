"""FCX Post-Capitulation Vol-Transition MR (FCX-011)"""

from trading.experiments import register
from trading.experiments.fcx_011_vol_transition_mr.strategy import FCX011Strategy

register("fcx_011_vol_transition_mr")(FCX011Strategy)
