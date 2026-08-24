"""SPY RSI(2) 極端超賣均值回歸 (SPY-004)"""

from trading.experiments import register
from trading.experiments.spy_004_rsi2_reversal.strategy import (
    SPYRsi2Strategy,
)

register("spy_004_rsi2_reversal")(SPYRsi2Strategy)
