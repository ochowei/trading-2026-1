"""FCX Relative Strength (FCX-006)"""

from trading.experiments import register
from trading.experiments.fcx_006_relative_strength.strategy import (
    FCXRelativeStrengthStrategy,
)

register("fcx_006_relative_strength")(FCXRelativeStrengthStrategy)
