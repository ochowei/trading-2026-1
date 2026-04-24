"""TLT Sustained Low-Volatility Regime Mean Reversion (TLT-012)"""

from trading.experiments import register
from trading.experiments.tlt_012_sustained_regime_mr.strategy import (
    TLT012SustainedRegimeMRStrategy,
)

register("tlt_012_sustained_regime_mr")(TLT012SustainedRegimeMRStrategy)
