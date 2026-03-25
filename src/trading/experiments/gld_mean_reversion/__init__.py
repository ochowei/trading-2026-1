"""
GLD Mean Reversion Experiment
"""

from trading.experiments import register
from trading.experiments.gld_mean_reversion.strategy import GLDMeanReversionStrategy

register("gld_mean_reversion")(GLDMeanReversionStrategy)
