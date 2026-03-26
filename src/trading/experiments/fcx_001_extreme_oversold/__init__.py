"""
FCX Extreme Oversold Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.fcx_001_extreme_oversold.strategy import FCXExtremeOversoldStrategy

register("fcx_001_extreme_oversold")(FCXExtremeOversoldStrategy)
