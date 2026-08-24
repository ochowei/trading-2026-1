"""TQQQ Post-Capitulation Vol-Transition MR (TQQQ-024)"""

from trading.experiments import register
from trading.experiments.tqqq_024_vol_transition_mr.strategy import (
    TQQQ024VolTransitionMRStrategy,
)

register("tqqq_024_vol_transition_mr")(TQQQ024VolTransitionMRStrategy)
