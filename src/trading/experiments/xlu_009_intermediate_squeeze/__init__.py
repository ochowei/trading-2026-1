"""XLU Intermediate BB Squeeze Breakout (XLU-009)"""

from trading.experiments import register
from trading.experiments.xlu_009_intermediate_squeeze.strategy import (
    XLU009Strategy,
)

register("xlu_009_intermediate_squeeze")(XLU009Strategy)
