"""CIBR 波動率自適應均值回歸 (CIBR-002)"""

from trading.experiments import register
from trading.experiments.cibr_002_vol_adaptive_mr.strategy import (
    CIBRVolAdaptiveMRStrategy,
)

register("cibr_002_vol_adaptive_mr")(CIBRVolAdaptiveMRStrategy)
