"""TQQQ Gap-Down 資本化 + 日內反轉均值回歸 (TQQQ-016)"""

from trading.experiments import register
from trading.experiments.tqqq_016_gap_reversal_mr.strategy import (
    TQQQ016Strategy,
)

register("tqqq_016_gap_reversal_mr")(TQQQ016Strategy)
