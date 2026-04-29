"""IBIT Range Expansion Climax Mean Reversion (IBIT-008)"""

from trading.experiments import register
from trading.experiments.ibit_008_range_expansion_mr.strategy import (
    IBIT008Strategy,
)

register("ibit_008_range_expansion_mr")(IBIT008Strategy)
