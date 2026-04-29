"""CIBR Higher-Low Structural Confirmation MR (CIBR-013)"""

from trading.experiments import register
from trading.experiments.cibr_013_higher_low_confirmation_mr.strategy import (
    CIBR013Strategy,
)

register("cibr_013_higher_low_confirmation_mr")(CIBR013Strategy)
