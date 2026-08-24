"""SIVR 回檔範圍 + Williams %R 均值回歸 (SIVR-005)"""

from trading.experiments import register
from trading.experiments.sivr_005_capped_pullback_wr.strategy import (
    SIVRCappedPullbackWRStrategy,
)

register("sivr_005_capped_pullback_wr")(SIVRCappedPullbackWRStrategy)
