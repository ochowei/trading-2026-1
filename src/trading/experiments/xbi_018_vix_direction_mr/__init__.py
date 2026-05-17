"""XBI ^VIX Implied-Vol DIRECTION Regime Gate Pullback MR (XBI-018)"""

from trading.experiments import register
from trading.experiments.xbi_018_vix_direction_mr.strategy import (
    XBI018VixDirectionMRStrategy,
)

register("xbi_018_vix_direction_mr")(XBI018VixDirectionMRStrategy)
