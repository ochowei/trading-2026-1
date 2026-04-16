"""VGK Volatility-Adaptive Pullback MR (VGK-002)"""

from trading.experiments import register
from trading.experiments.vgk_002_vol_adaptive_pullback.strategy import VGK002Strategy

register("vgk_002_vol_adaptive_pullback")(VGK002Strategy)
