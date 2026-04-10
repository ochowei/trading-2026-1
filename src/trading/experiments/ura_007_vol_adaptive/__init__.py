"""URA 波動率自適應均值回歸 (URA-007)"""

from trading.experiments import register
from trading.experiments.ura_007_vol_adaptive.strategy import (
    URA007Strategy,
)

register("ura_007_vol_adaptive")(URA007Strategy)
