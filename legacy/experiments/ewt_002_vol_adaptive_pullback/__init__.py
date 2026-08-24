"""EWT Volatility-Adaptive Pullback MR (EWT-002)"""

from trading.experiments import register
from trading.experiments.ewt_002_vol_adaptive_pullback.strategy import EWT002Strategy

register("ewt_002_vol_adaptive_pullback")(EWT002Strategy)
