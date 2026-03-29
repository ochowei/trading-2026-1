"""
FCX Optimized Exit Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.fcx_003_optimized_exit.strategy import FCXOptimizedExitStrategy

register("fcx_003_optimized_exit")(FCXOptimizedExitStrategy)
