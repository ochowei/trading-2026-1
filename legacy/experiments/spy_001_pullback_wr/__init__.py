"""SPY 回檔 + Williams %R + 反轉K線 均值回歸 (SPY-001)"""

from trading.experiments import register
from trading.experiments.spy_001_pullback_wr.strategy import (
    SPYPullbackWRStrategy,
)

register("spy_001_pullback_wr")(SPYPullbackWRStrategy)
