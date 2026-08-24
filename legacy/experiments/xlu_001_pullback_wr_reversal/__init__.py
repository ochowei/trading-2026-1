"""XLU 回檔 + Williams %R + 反轉K線 均值回歸 (XLU-001)"""

from trading.experiments import register
from trading.experiments.xlu_001_pullback_wr_reversal.strategy import (
    XLUPullbackWRReversalStrategy,
)

register("xlu_001_pullback_wr_reversal")(XLUPullbackWRReversalStrategy)
