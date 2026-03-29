"""SIVR 收盤位置過濾 + 回檔範圍 + Williams %R 均值回歸 (SIVR-006)"""

from trading.experiments import register
from trading.experiments.sivr_006_closepos_pullback_wr.strategy import (
    SIVRClosePosStrategy,
)

register("sivr_006_closepos_pullback_wr")(SIVRClosePosStrategy)
