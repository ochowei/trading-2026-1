"""TSLA 回檔後動量回復 (TSLA-011)"""

from trading.experiments import register
from trading.experiments.tsla_011_momentum_recovery.strategy import (
    TSLAMomentumRecoveryStrategy,
)

register("tsla_011_momentum_recovery")(TSLAMomentumRecoveryStrategy)
