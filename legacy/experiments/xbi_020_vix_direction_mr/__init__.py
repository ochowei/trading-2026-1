"""XBI ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR (XBI-020)"""

from trading.experiments import register
from trading.experiments.xbi_020_vix_direction_mr.strategy import (
    XBI020VixDirectionMRStrategy,
)

register("xbi_020_vix_direction_mr")(XBI020VixDirectionMRStrategy)
