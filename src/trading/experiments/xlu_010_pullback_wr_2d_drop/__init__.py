"""XLU Pullback + Williams %R + 2-Day Drop (XLU-010)"""

from trading.experiments import register
from trading.experiments.xlu_010_pullback_wr_2d_drop.strategy import (
    XLUPullbackWR2dDropStrategy,
)

register("xlu_010_pullback_wr_2d_drop")(XLUPullbackWR2dDropStrategy)
