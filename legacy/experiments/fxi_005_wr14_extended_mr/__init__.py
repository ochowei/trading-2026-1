"""FXI WR(14) Extended Cooldown MR (FXI-005)"""

from trading.experiments import register
from trading.experiments.fxi_005_wr14_extended_mr.strategy import FXI005Strategy

register("fxi_005_wr14_extended_mr")(FXI005Strategy)
