"""NVDA RS Exit Optimization (NVDA-007)"""

from trading.experiments import register
from trading.experiments.nvda_007_rs_exit_optimized.strategy import (
    NVDARSExitOptimizedStrategy,
)

register("nvda_007_rs_exit_optimized")(NVDARSExitOptimizedStrategy)
