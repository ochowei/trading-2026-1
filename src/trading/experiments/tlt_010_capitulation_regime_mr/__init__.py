"""TLT Capitulation-Confirmed Vol-Regime-Gated Mean Reversion (TLT-010)"""

from trading.experiments import register
from trading.experiments.tlt_010_capitulation_regime_mr.strategy import (
    TLT010CapitulationRegimeMRStrategy,
)

register("tlt_010_capitulation_regime_mr")(TLT010CapitulationRegimeMRStrategy)
