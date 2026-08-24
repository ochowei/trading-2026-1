"""NVDA Multi-Week Regime-Aware Momentum Breakout Pullback Continuation (NVDA-013)"""

from trading.experiments import register
from trading.experiments.nvda_013_regime_mbpc.strategy import (
    NVDA013RegimeMBPCStrategy,
)

register("nvda_013_regime_mbpc")(NVDA013RegimeMBPCStrategy)
