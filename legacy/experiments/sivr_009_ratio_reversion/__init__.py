"""SIVR Gold/Silver Ratio Mean Reversion (SIVR-009)"""

from trading.experiments import register
from trading.experiments.sivr_009_ratio_reversion.strategy import (
    SIVRRatioReversionStrategy,
)

register("sivr_009_ratio_reversion")(SIVRRatioReversionStrategy)
