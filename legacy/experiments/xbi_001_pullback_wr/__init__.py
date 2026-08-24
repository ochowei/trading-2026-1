"""XBI 回檔 + Williams %R 均值回歸 (XBI-001)"""

from trading.experiments import register
from trading.experiments.xbi_001_pullback_wr.strategy import (
    XBIPullbackWRStrategy,
)

register("xbi_001_pullback_wr")(XBIPullbackWRStrategy)
