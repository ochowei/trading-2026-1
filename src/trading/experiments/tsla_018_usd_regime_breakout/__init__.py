"""TSLA TSLA-USD (UUP) Direction Regime-Gated BB Squeeze Breakout (TSLA-018)"""

from trading.experiments import register
from trading.experiments.tsla_018_usd_regime_breakout.strategy import (
    TSLA018USDRegimeBreakoutStrategy,
)

register("tsla_018_usd_regime_breakout")(TSLA018USDRegimeBreakoutStrategy)
