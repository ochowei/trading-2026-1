"""TSM Pairs Trading TSM/NVDA (TSM-009)"""

from trading.experiments import register
from trading.experiments.tsm_009_pairs_trading.strategy import (
    TSMPairsTradingStrategy,
)

register("tsm_009_pairs_trading")(TSMPairsTradingStrategy)
