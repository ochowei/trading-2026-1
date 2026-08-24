"""USO 回檔 + Williams %R 均值回歸 (USO-001)"""

from trading.experiments import register
from trading.experiments.uso_001_pullback_wr.strategy import (
    USOPullbackWRStrategy,
)

register("uso_001_pullback_wr")(USOPullbackWRStrategy)
