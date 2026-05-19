"""TSLA TSLA-USD (UUP) Direction Regime-Gated BB Squeeze Breakout (TSLA-020)"""

from trading.experiments import register
from trading.experiments.tsla_020_usd_regime_breakout.strategy import (
    TSLA020USDRegimeBreakoutStrategy,
)

register("tsla_020_usd_regime_breakout")(TSLA020USDRegimeBreakoutStrategy)
