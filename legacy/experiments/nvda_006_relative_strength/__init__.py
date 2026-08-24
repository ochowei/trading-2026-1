"""NVDA Relative Strength Momentum Pullback (NVDA-006)"""

from trading.experiments import register
from trading.experiments.nvda_006_relative_strength.strategy import (
    NVDARelativeStrengthStrategy,
)

register("nvda_006_relative_strength")(NVDARelativeStrengthStrategy)
