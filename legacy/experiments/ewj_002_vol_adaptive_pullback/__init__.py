"""EWJ Volatility-Adaptive Pullback MR (EWJ-002)"""

from trading.experiments import register
from trading.experiments.ewj_002_vol_adaptive_pullback.strategy import EWJ002Strategy

register("ewj_002_vol_adaptive_pullback")(EWJ002Strategy)
