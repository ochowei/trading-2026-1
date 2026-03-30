"""IBIT 回檔 + Williams %R 均值回歸 (IBIT-001)"""

from trading.experiments import register
from trading.experiments.ibit_001_pullback_wr.strategy import (
    IBITPullbackWRStrategy,
)

register("ibit_001_pullback_wr")(IBITPullbackWRStrategy)
