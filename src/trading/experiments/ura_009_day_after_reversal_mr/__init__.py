"""URA Day-After Capitulation Mean Reversion (URA-009)"""

from trading.experiments import register
from trading.experiments.ura_009_day_after_reversal_mr.strategy import (
    URADayAfterReversalMRStrategy,
)

register("ura_009_day_after_reversal_mr")(URADayAfterReversalMRStrategy)
