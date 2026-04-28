"""CIBR Post-Capitulation Vol-Transition MR (CIBR-012)"""

from trading.experiments import register
from trading.experiments.cibr_012_vol_transition_mr.strategy import (
    CIBR012Strategy,
)

register("cibr_012_vol_transition_mr")(CIBR012Strategy)
