"""SIVR 急跌 + RSI(5) 均值回歸 (SIVR-011)"""

from trading.experiments import register
from trading.experiments.sivr_011_sharp_decline_rsi5.strategy import (
    SIVRSharpDeclineRSI5Strategy,
)

register("sivr_011_sharp_decline_rsi5")(SIVRSharpDeclineRSI5Strategy)
