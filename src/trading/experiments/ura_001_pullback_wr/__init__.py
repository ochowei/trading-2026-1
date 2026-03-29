"""URA 回檔 + Williams %R 均值回歸 (URA-001)"""

from trading.experiments import register
from trading.experiments.ura_001_pullback_wr.strategy import (
    URAPullbackWRStrategy,
)

register("ura_001_pullback_wr")(URAPullbackWRStrategy)
