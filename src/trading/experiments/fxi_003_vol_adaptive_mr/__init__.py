"""FXI Vol-Adaptive Mean Reversion (FXI-003)"""

from trading.experiments import register
from trading.experiments.fxi_003_vol_adaptive_mr.strategy import FXI003Strategy

register("fxi_003_vol_adaptive_mr")(FXI003Strategy)
