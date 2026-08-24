"""TSLA TSLA-QQQ Cross-Asset Divergence Regime-Gated BB Squeeze Breakout (TSLA-017)"""

from trading.experiments import register
from trading.experiments.tsla_017_qqq_divergence_breakout.strategy import (
    TSLA017QQQDivergenceBreakoutStrategy,
)

register("tsla_017_qqq_divergence_breakout")(TSLA017QQQDivergenceBreakoutStrategy)
