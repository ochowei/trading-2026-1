"""
TSLA Extreme Oversold Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.tsla_001_extreme_oversold.strategy import TSLAExtremeOversoldStrategy

register("tsla_001_extreme_oversold")(TSLAExtremeOversoldStrategy)
