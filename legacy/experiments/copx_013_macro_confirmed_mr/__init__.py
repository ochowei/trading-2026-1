"""COPX Macro-Confirmed Vol-Adaptive Capitulation MR (COPX-013)"""

from trading.experiments import register
from trading.experiments.copx_013_macro_confirmed_mr.strategy import (
    COPX013Strategy,
)

register("copx_013_macro_confirmed_mr")(COPX013Strategy)
