"""INDA 回檔 + Williams %R + 反轉K線 均值回歸 (INDA-001)"""

from trading.experiments import register
from trading.experiments.inda_001_pullback_wr_reversal.strategy import (
    INDAPullbackWRReversalStrategy,
)

register("inda_001_pullback_wr_reversal")(INDAPullbackWRReversalStrategy)
