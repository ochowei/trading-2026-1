"""USO 波動率自適應均值回歸 (USO-023)"""

from trading.experiments import register
from trading.experiments.uso_023_vol_adaptive_mr.strategy import (
    USO023Strategy,
)

register("uso_023_vol_adaptive_mr")(USO023Strategy)
