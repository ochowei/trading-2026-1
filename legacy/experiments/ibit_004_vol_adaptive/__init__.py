"""IBIT 波動率自適應均值回歸 (IBIT-004)"""

from trading.experiments import register
from trading.experiments.ibit_004_vol_adaptive.strategy import (
    IBIT004Strategy,
)

register("ibit_004_vol_adaptive")(IBIT004Strategy)
