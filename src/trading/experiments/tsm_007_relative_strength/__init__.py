"""TSM Relative Strength Momentum Pullback (TSM-007)"""

from trading.experiments import register
from trading.experiments.tsm_007_relative_strength.strategy import (
    TSMRelativeStrengthStrategy,
)

register("tsm_007_relative_strength")(TSMRelativeStrengthStrategy)
