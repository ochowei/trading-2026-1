"""NVDA Negative Relative Strength Mean Reversion (NVDA-014)"""

from trading.experiments import register
from trading.experiments.nvda_014_negative_rs_mr.strategy import (
    NVDANegativeRSMRStrategy,
)

register("nvda_014_negative_rs_mr")(NVDANegativeRSMRStrategy)
