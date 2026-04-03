"""NVDA BB Squeeze Optimized (NVDA-004)"""

from trading.experiments import register
from trading.experiments.nvda_004_bb_squeeze_optimized.strategy import (
    NVDABBSqueezeOptimizedStrategy,
)

register("nvda_004_bb_squeeze_optimized")(NVDABBSqueezeOptimizedStrategy)
