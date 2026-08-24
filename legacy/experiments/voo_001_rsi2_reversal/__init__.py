"""VOO RSI(2) 極端超賣均值回歸 (VOO-001)"""

from trading.experiments import register
from trading.experiments.voo_001_rsi2_reversal.strategy import (
    VOORsi2Strategy,
)

register("voo_001_rsi2_reversal")(VOORsi2Strategy)
