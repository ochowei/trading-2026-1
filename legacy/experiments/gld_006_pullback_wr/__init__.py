"""GLD 回檔 + Williams %R 均值回歸 (GLD-006)"""

from trading.experiments import register
from trading.experiments.gld_006_pullback_wr.strategy import (
    GLDPullbackWRStrategy,
)

register("gld_006_pullback_wr")(GLDPullbackWRStrategy)
