"""EEM Volatility-Adaptive RSI(2) Mean Reversion (EEM-002)"""

from trading.experiments import register
from trading.experiments.eem_002_vol_adaptive_rsi2.strategy import (
    EEM002Strategy,
)

register("eem_002_vol_adaptive_rsi2")(EEM002Strategy)
