"""SIVR 回檔 + Williams %R 均值回歸 (SIVR-003)"""

from trading.experiments import register
from trading.experiments.sivr_003_pullback_wr.strategy import (
    SIVRPullbackWRStrategy,
)

register("sivr_003_pullback_wr")(SIVRPullbackWRStrategy)
