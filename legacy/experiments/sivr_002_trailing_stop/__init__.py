"""SIVR 追蹤停損均值回歸 (SIVR-002)"""

from trading.experiments import register
from trading.experiments.sivr_002_trailing_stop.strategy import SIVRTrailingStopStrategy

register("sivr_002_trailing_stop")(SIVRTrailingStopStrategy)
