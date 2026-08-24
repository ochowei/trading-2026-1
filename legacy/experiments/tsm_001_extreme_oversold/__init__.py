"""
TSM Extreme Oversold Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.tsm_001_extreme_oversold.strategy import TSMExtremeOversoldStrategy

register("tsm_001_extreme_oversold")(TSMExtremeOversoldStrategy)
