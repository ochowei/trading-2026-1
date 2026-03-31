"""DIA RSI(2) 收窄停損均值回歸 (DIA-005)"""

from trading.experiments import register
from trading.experiments.dia_005_tighter_sl.strategy import (
    DIARsi2TighterSLStrategy,
)

register("dia_005_tighter_sl")(DIARsi2TighterSLStrategy)
