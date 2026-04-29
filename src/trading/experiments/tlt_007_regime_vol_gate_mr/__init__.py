"""TLT Volatility-Regime-Gated Mean Reversion (TLT-007)"""

from trading.experiments import register
from trading.experiments.tlt_007_regime_vol_gate_mr.strategy import (
    TLT007RegimeVolGateMRStrategy,
)

register("tlt_007_regime_vol_gate_mr")(TLT007RegimeVolGateMRStrategy)
