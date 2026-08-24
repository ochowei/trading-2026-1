"""COPX 波動率自適應均值回歸 (COPX-007)"""

from trading.experiments import register
from trading.experiments.copx_007_vol_adaptive.strategy import (
    COPX007Strategy,
)

register("copx_007_vol_adaptive")(COPX007Strategy)
