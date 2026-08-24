"""SIVR 極端超賣均值回歸 (SIVR-001)"""

from trading.experiments import register
from trading.experiments.sivr_001_mean_reversion.strategy import SIVRMeanReversionStrategy

register("sivr_001_mean_reversion")(SIVRMeanReversionStrategy)
