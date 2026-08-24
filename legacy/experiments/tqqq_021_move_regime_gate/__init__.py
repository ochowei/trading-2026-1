"""TQQQ ^MOVE Bond-Vol Regime Gate on Vol-Regime-Gated Capitulation Buy (TQQQ-021)"""

from trading.experiments import register
from trading.experiments.tqqq_021_move_regime_gate.strategy import (
    TQQQ021MoveRegimeStrategy,
)

register("tqqq_021_move_regime_gate")(TQQQ021MoveRegimeStrategy)
