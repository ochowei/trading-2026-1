"""FXI Volatility-Adaptive Pullback MR (FXI-002)"""

from trading.experiments import register
from trading.experiments.fxi_002_vol_adaptive_pullback.strategy import FXI002Strategy

register("fxi_002_vol_adaptive_pullback")(FXI002Strategy)
