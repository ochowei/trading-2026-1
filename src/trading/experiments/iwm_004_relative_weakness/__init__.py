"""IWM RSI(2) TP +4.0% 測試 (IWM-004)"""

from trading.experiments import register
from trading.experiments.iwm_004_relative_weakness.strategy import (
    IWM004Strategy,
)

register("iwm_004_relative_weakness")(IWM004Strategy)
