"""FXI Failed Breakdown Reversal / Turtle Soup (FXI-009)"""

from trading.experiments import register
from trading.experiments.fxi_009_failed_breakdown_reversal.strategy import FXI009Strategy

register("fxi_009_failed_breakdown_reversal")(FXI009Strategy)
