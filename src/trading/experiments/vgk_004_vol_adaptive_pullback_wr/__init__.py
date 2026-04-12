"""VGK 波動率自適應回檔+WR 均值回歸 (VGK-004)"""

from trading.experiments import register
from trading.experiments.vgk_004_vol_adaptive_pullback_wr.strategy import (
    VGK004Strategy,
)

register("vgk_004_vol_adaptive_pullback_wr")(VGK004Strategy)
