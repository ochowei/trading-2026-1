"""TLT 回檔 + Williams %R + 反轉K線 均值回歸 (TLT-001)"""

from trading.experiments import register
from trading.experiments.tlt_001_pullback_wr_reversal.strategy import (
    TLTPullbackWRReversalStrategy,
)

register("tlt_001_pullback_wr_reversal")(TLTPullbackWRReversalStrategy)
