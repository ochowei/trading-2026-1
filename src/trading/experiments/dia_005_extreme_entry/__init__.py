"""DIA RSI(2) 延長持倉均值回歸 (DIA-005)"""

from trading.experiments import register
from trading.experiments.dia_005_extreme_entry.strategy import (
    DIAExtendedHoldStrategy,
)

register("dia_005_extreme_entry")(DIAExtendedHoldStrategy)
