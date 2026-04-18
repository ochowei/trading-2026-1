"""IBIT Gap-Down 資本化 + 日內反轉均值回歸 (IBIT-006)"""

from trading.experiments import register
from trading.experiments.ibit_006_gap_reversal_mr.strategy import (
    IBIT006Strategy,
)

register("ibit_006_gap_reversal_mr")(IBIT006Strategy)
