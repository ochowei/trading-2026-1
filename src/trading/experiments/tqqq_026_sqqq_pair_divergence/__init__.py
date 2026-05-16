"""TQQQ/SQQQ Inverse-Pair Capitulation Confirmation (TQQQ-026)"""

from trading.experiments import register
from trading.experiments.tqqq_026_sqqq_pair_divergence.strategy import (
    TQQQ026SqqqPairStrategy,
)

register("tqqq_026_sqqq_pair_divergence")(TQQQ026SqqqPairStrategy)
