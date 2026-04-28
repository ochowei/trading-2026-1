"""XBI Post-Capitulation Vol-Transition MR (XBI-014)"""

from trading.experiments import register
from trading.experiments.xbi_014_vol_transition_mr.strategy import (
    XBI014Strategy,
)

register("xbi_014_vol_transition_mr")(XBI014Strategy)
