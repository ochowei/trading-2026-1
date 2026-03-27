"""
DIA Pullback + Williams %R + Reversal Candle Experiment
"""

from trading.experiments import register
from trading.experiments.dia_001_pullback_wr_reversal.strategy import (
    DIAPullbackWRReversalStrategy,
)

register("dia_001_pullback_wr_reversal")(DIAPullbackWRReversalStrategy)
