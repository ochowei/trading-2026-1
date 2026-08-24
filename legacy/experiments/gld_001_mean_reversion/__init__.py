"""
GLD Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.gld_001_mean_reversion.strategy import GLDMeanReversionStrategy

register("gld_001_mean_reversion")(GLDMeanReversionStrategy)
