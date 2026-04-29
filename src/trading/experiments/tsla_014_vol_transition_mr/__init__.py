"""TSLA Post-Capitulation Vol-Transition MR (TSLA-014)"""

from trading.experiments import register
from trading.experiments.tsla_014_vol_transition_mr.strategy import (
    TSLA014Strategy,
)

register("tsla_014_vol_transition_mr")(TSLA014Strategy)
