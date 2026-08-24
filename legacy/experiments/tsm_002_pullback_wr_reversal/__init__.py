"""
TSM Pullback + Williams %R + Reversal Candle Experiment
"""

from trading.experiments import register
from trading.experiments.tsm_002_pullback_wr_reversal.strategy import (
    TSMPullbackWRReversalStrategy,
)

register("tsm_002_pullback_wr_reversal")(TSMPullbackWRReversalStrategy)
