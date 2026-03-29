"""TSM RSI(2) 極端超賣均值回歸 (TSM-003)"""

from trading.experiments import register
from trading.experiments.tsm_003_rsi2_reversal.strategy import (
    TSMRsi2Strategy,
)

register("tsm_003_rsi2_reversal")(TSMRsi2Strategy)
