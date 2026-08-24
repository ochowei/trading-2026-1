"""VGK 2日急跌增強回檔+WR+ATR 均值回歸 (VGK-005)"""

from trading.experiments import register
from trading.experiments.vgk_005_decline_enhanced_mr.strategy import (
    VGK005Strategy,
)

register("vgk_005_decline_enhanced_mr")(VGK005Strategy)
