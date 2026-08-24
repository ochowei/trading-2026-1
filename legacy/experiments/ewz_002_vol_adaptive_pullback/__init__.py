"""EWZ Volatility-Adaptive Pullback MR (EWZ-002)"""

from trading.experiments import register
from trading.experiments.ewz_002_vol_adaptive_pullback.strategy import EWZ002Strategy

register("ewz_002_vol_adaptive_pullback")(EWZ002Strategy)
