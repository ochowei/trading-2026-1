"""EWZ 回檔 + Williams %R 均值回歸 (EWZ-001)"""

from trading.experiments import register
from trading.experiments.ewz_001_pullback_wr.strategy import (
    EWZPullbackWRStrategy,
)

register("ewz_001_pullback_wr")(EWZPullbackWRStrategy)
