"""INDA Post-Capitulation Vol-Transition MR (INDA-010)"""

from trading.experiments import register
from trading.experiments.inda_010_vol_transition_mr.strategy import (
    INDA010Strategy,
)

register("inda_010_vol_transition_mr")(INDA010Strategy)
