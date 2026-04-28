"""TLT Day-After Capitulation Mean Reversion (TLT-006)"""

from trading.experiments import register
from trading.experiments.tlt_006_day_after_reversal_mr.strategy import (
    TLTDayAfterReversalMRStrategy,
)

register("tlt_006_day_after_reversal_mr")(TLTDayAfterReversalMRStrategy)
