"""DIA RSI(2) 極端超賣均值回歸 (DIA-002)"""

from trading.experiments import register
from trading.experiments.dia_002_rsi2_reversal.strategy import (
    DIARsi2Strategy,
)

register("dia_002_rsi2_reversal")(DIARsi2Strategy)
