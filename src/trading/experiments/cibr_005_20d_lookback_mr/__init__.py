"""CIBR 20日回看窗口均值回歸 (CIBR-005)"""

from trading.experiments import register
from trading.experiments.cibr_005_20d_lookback_mr.strategy import (
    CIBR20DLookbackMRStrategy,
)

register("cibr_005_20d_lookback_mr")(CIBR20DLookbackMRStrategy)
