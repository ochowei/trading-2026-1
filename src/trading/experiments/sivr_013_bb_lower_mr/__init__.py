"""SIVR Bollinger Band 下軌均值回歸 (SIVR-013)"""

from trading.experiments import register
from trading.experiments.sivr_013_bb_lower_mr.strategy import (
    SIVR013Strategy,
)

register("sivr_013_bb_lower_mr")(SIVR013Strategy)
