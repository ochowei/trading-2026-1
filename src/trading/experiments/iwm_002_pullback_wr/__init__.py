"""IWM 回檔 + Williams %R 均值回歸 (IWM-002)"""

from trading.experiments import register
from trading.experiments.iwm_002_pullback_wr.strategy import (
    IWMPullbackWRStrategy,
)

register("iwm_002_pullback_wr")(IWMPullbackWRStrategy)
