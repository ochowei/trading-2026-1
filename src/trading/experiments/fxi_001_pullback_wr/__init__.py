"""FXI 回檔 + Williams %R 均值回歸 (FXI-001)"""

from trading.experiments import register
from trading.experiments.fxi_001_pullback_wr.strategy import (
    FXIPullbackWRStrategy,
)

register("fxi_001_pullback_wr")(FXIPullbackWRStrategy)
