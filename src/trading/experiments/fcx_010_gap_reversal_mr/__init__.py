"""FCX Gap-Down 資本化 + 日內反轉均值回歸 (FCX-010)"""

from trading.experiments import register
from trading.experiments.fcx_010_gap_reversal_mr.strategy import (
    FCX010Strategy,
)

register("fcx_010_gap_reversal_mr")(FCX010Strategy)
