"""FXI Connor's RSI Mean Reversion (FXI-011)"""

from trading.experiments import register
from trading.experiments.fxi_011_connors_rsi_mr.strategy import FXI011Strategy

register("fxi_011_connors_rsi_mr")(FXI011Strategy)
