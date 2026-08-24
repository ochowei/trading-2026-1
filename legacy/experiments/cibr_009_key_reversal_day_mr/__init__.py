"""CIBR Key Reversal Day after Pullback (CIBR-009)"""

from trading.experiments import register
from trading.experiments.cibr_009_key_reversal_day_mr.strategy import (
    CIBR009Strategy,
)

register("cibr_009_key_reversal_day_mr")(CIBR009Strategy)
