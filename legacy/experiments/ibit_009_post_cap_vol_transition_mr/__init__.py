"""IBIT Post-Capitulation Vol-Transition MR (IBIT-009)"""

from trading.experiments import register
from trading.experiments.ibit_009_post_cap_vol_transition_mr.strategy import (
    IBIT009Strategy,
)

register("ibit_009_post_cap_vol_transition_mr")(IBIT009Strategy)
