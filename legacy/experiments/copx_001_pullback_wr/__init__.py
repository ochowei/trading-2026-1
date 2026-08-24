"""COPX 回檔 + Williams %R 均值回歸 (COPX-001)"""

from trading.experiments import register
from trading.experiments.copx_001_pullback_wr.strategy import (
    COPXPullbackWRStrategy,
)

register("copx_001_pullback_wr")(COPXPullbackWRStrategy)
