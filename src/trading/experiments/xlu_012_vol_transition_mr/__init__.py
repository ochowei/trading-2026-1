"""XLU Post-Capitulation Vol-Transition MR (XLU-012)"""

from trading.experiments import register
from trading.experiments.xlu_012_vol_transition_mr.strategy import (
    XLU012Strategy,
)

register("xlu_012_vol_transition_mr")(XLU012Strategy)
