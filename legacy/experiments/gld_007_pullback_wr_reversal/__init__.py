"""GLD 回檔 + Williams %R + 反轉K線 均值回歸 (GLD-007)"""

from trading.experiments import register
from trading.experiments.gld_007_pullback_wr_reversal.strategy import (
    GLDPullbackWRReversalStrategy,
)

register("gld_007_pullback_wr_reversal")(GLDPullbackWRReversalStrategy)
