"""FXI USDCNH Direction Filter on Cross-Asset Divergence MR (FXI-016)"""

from trading.experiments import register
from trading.experiments.fxi_016_usdcnh_direction_mr.strategy import FXI016Strategy

register("fxi_016_usdcnh_direction_mr")(FXI016Strategy)
