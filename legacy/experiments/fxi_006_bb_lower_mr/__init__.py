"""FXI BB Lower Band Mean Reversion (FXI-006)"""

from trading.experiments import register
from trading.experiments.fxi_006_bb_lower_mr.strategy import FXI006Strategy

register("fxi_006_bb_lower_mr")(FXI006Strategy)
