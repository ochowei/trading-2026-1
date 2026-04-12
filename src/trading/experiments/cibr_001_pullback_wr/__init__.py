"""CIBR 回檔 + Williams %R 均值回歸 (CIBR-001)"""

from trading.experiments import register
from trading.experiments.cibr_001_pullback_wr.strategy import (
    CIBRPullbackWRStrategy,
)

register("cibr_001_pullback_wr")(CIBRPullbackWRStrategy)
