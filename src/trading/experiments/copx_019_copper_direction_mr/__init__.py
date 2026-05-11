"""COPX HG=F (Copper Futures) Direction Filter on Volume-Confirmed MR (COPX-019)"""

from trading.experiments import register
from trading.experiments.copx_019_copper_direction_mr.strategy import (
    COPX019CopperDirectionMRStrategy,
)

register("copx_019_copper_direction_mr")(COPX019CopperDirectionMRStrategy)
