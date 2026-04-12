"""EWT 回檔 + Williams %R + 反轉K線 均值回歸 (EWT-001)"""

from trading.experiments import register
from trading.experiments.ewt_001_pullback_wr_reversal.strategy import (
    EWTPullbackWRReversalStrategy,
)

register("ewt_001_pullback_wr_reversal")(EWTPullbackWRReversalStrategy)
