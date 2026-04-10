"""DIA Volatility-Adaptive RSI(2) Mean Reversion (DIA-011)"""

from trading.experiments import register
from trading.experiments.dia_011_vol_adaptive_rsi2.strategy import (
    DIA011Strategy,
)

register("dia_011_vol_adaptive_rsi2")(DIA011Strategy)
