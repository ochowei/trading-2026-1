"""IWM RSI(2) 極端超賣均值回歸 (IWM-001)"""

from trading.experiments import register
from trading.experiments.iwm_001_rsi2_reversal.strategy import (
    IWMRsi2Strategy,
)

register("iwm_001_rsi2_reversal")(IWMRsi2Strategy)
