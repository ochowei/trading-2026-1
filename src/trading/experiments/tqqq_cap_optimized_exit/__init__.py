"""TQQQ 優化出場實驗 (TQQQ Optimized Exit Experiment)"""

from trading.experiments import register
from trading.experiments.tqqq_cap_optimized_exit.strategy import TQQQCapOptimizedExitStrategy

register("tqqq_cap_optimized_exit")(TQQQCapOptimizedExitStrategy)
