"""CIBR BB 下軌均值回歸 (CIBR-007)"""

from trading.experiments import register
from trading.experiments.cibr_007_bb_lower_mr.strategy import (
    CIBRBBLowerMRStrategy,
)

register("cibr_007_bb_lower_mr")(CIBRBBLowerMRStrategy)
