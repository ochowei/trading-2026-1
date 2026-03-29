"""DIA RSI(2) 非對稱出場均值回歸 (DIA-003)"""

from trading.experiments import register
from trading.experiments.dia_003_rsi2_bb.strategy import (
    DIARsi2AsymStrategy,
)

register("dia_003_rsi2_bb")(DIARsi2AsymStrategy)
