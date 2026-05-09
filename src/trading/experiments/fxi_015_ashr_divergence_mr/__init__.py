"""FXI-ASHR Cross-Asset Divergence Filter on ATR-Band MR (FXI-015)"""

from trading.experiments import register
from trading.experiments.fxi_015_ashr_divergence_mr.strategy import FXI015Strategy

register("fxi_015_ashr_divergence_mr")(FXI015Strategy)
