"""COPX Post-Capitulation Vol-Transition MR (COPX-010)"""

from trading.experiments import register
from trading.experiments.copx_010_vol_transition_mr.strategy import (
    COPX010Strategy,
)

register("copx_010_vol_transition_mr")(COPX010Strategy)
