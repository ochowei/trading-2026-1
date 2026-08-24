"""TSM RS Exit Optimization (TSM-008)"""

from trading.experiments import register
from trading.experiments.tsm_008_rs_exit_optimization.strategy import (
    TSMRSExitOptStrategy,
)

register("tsm_008_rs_exit_optimization")(TSMRSExitOptStrategy)
