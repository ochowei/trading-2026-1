"""
NVDA Extreme Oversold Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.nvda_001_extreme_oversold.strategy import NVDAExtremeOversoldStrategy

register("nvda_001_extreme_oversold")(NVDAExtremeOversoldStrategy)
