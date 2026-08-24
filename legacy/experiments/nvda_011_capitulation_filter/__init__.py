"""NVDA Capitulation-Depth Filter MR (NVDA-011)"""

from trading.experiments import register
from trading.experiments.nvda_011_capitulation_filter.strategy import (
    NVDA011Strategy,
)

register("nvda_011_capitulation_filter")(NVDA011Strategy)
