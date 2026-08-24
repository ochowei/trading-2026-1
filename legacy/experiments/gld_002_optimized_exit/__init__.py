"""GLD 優化出場均值回歸 (GLD Optimized Exit Mean Reversion) — GLD-002"""

from trading.experiments import register
from trading.experiments.gld_002_optimized_exit.strategy import GLDOptimizedExitStrategy

register("gld_002_optimized_exit")(GLDOptimizedExitStrategy)
