"""SOXL Volatility-Regime-Gated Capitulation Buy (SOXL-012)"""

from trading.experiments import register
from trading.experiments.soxl_012_regime_vol_gate.strategy import (
    SOXL012RegimeVolGateStrategy,
)

register("soxl_012_regime_vol_gate")(SOXL012RegimeVolGateStrategy)
