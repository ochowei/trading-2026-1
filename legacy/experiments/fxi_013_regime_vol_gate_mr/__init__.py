"""FXI Volatility-Regime-Gated Mean Reversion (FXI-013)"""

from trading.experiments import register
from trading.experiments.fxi_013_regime_vol_gate_mr.strategy import (
    FXI013RegimeVolGateMRStrategy,
)

register("fxi_013_regime_vol_gate_mr")(FXI013RegimeVolGateMRStrategy)
