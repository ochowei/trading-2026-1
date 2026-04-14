"""VGK Volatility-Adaptive RSI(2) Mean Reversion (VGK-002)"""

from trading.experiments import register
from trading.experiments.vgk_002_vol_adaptive_rsi2.strategy import (
    VGK002Strategy,
)

register("vgk_002_vol_adaptive_rsi2")(VGK002Strategy)
