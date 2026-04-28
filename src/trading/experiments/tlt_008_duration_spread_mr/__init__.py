"""TLT Duration-Spread Mean Reversion (TLT-008)"""

from trading.experiments import register
from trading.experiments.tlt_008_duration_spread_mr.strategy import (
    TLT008DurationSpreadMRStrategy,
)

register("tlt_008_duration_spread_mr")(TLT008DurationSpreadMRStrategy)
