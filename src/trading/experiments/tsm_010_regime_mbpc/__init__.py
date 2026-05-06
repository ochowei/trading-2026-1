"""TSM Multi-Week Regime-Aware Momentum Breakout Pullback Continuation (TSM-010)"""

from trading.experiments import register
from trading.experiments.tsm_010_regime_mbpc.strategy import (
    TSM010RegimeMBPCStrategy,
)

register("tsm_010_regime_mbpc")(TSM010RegimeMBPCStrategy)
