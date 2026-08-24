"""TQQQ Volatility-Regime-Gated Capitulation Buy (TQQQ-018)"""

from trading.experiments import register
from trading.experiments.tqqq_018_regime_vol_gate.strategy import (
    TQQQ018RegimeVolGateStrategy,
)

register("tqqq_018_regime_vol_gate")(TQQQ018RegimeVolGateStrategy)
