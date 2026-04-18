"""FXI Relative Strength Momentum Pullback (FXI-007)"""

from trading.experiments import register
from trading.experiments.fxi_007_rs_momentum.strategy import FXI007Strategy

register("fxi_007_rs_momentum")(FXI007Strategy)
