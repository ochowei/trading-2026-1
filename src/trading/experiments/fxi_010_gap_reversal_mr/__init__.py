"""FXI Gap-Down Capitulation + Intraday Reversal MR (FXI-010)"""

from trading.experiments import register
from trading.experiments.fxi_010_gap_reversal_mr.strategy import FXI010Strategy

register("fxi_010_gap_reversal_mr")(FXI010Strategy)
