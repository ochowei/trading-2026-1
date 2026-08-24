"""VGK 回檔 + Williams %R 均值回歸 (VGK-003)"""

from trading.experiments import register
from trading.experiments.vgk_003_pullback_wr.strategy import (
    VGK003Strategy,
)

register("vgk_003_pullback_wr")(VGK003Strategy)
