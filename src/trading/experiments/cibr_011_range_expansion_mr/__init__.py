"""CIBR Range Expansion Climax Mean Reversion (CIBR-011)"""

from trading.experiments import register
from trading.experiments.cibr_011_range_expansion_mr.strategy import (
    CIBR011Strategy,
)

register("cibr_011_range_expansion_mr")(CIBR011Strategy)
