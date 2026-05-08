"""NVDA Failed Breakdown Reversal Mean Reversion (NVDA-019)"""

from trading.experiments import register
from trading.experiments.nvda_019_failed_breakdown_mr.strategy import (
    NVDA019FailedBreakdownStrategy,
)

register("nvda_019_failed_breakdown_mr")(NVDA019FailedBreakdownStrategy)
