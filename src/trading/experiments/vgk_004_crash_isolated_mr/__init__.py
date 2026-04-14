"""VGK 崩盤隔離回檔+WR+ATR 均值回歸 (VGK-004)"""

from trading.experiments import register
from trading.experiments.vgk_004_crash_isolated_mr.strategy import (
    VGK004Strategy,
)

register("vgk_004_crash_isolated_mr")(VGK004Strategy)
