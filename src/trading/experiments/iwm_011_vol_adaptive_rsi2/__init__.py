"""IWM Volatility-Adaptive RSI(2) Mean Reversion (IWM-011)"""

from trading.experiments import register
from trading.experiments.iwm_011_vol_adaptive_rsi2.strategy import (
    IWM011Strategy,
)

register("iwm_011_vol_adaptive_rsi2")(IWM011Strategy)
