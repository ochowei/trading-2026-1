"""IWM RSI(2) 極端超賣均值回歸（出場優化）(IWM-003)"""

from trading.experiments import register
from trading.experiments.iwm_003_rsi2_optimized.strategy import (
    IWMRsi2OptStrategy,
)

register("iwm_003_rsi2_optimized")(IWMRsi2OptStrategy)
