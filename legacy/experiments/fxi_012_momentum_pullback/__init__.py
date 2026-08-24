"""FXI Momentum Breakout Pullback Continuation (FXI-012)"""

from trading.experiments import register
from trading.experiments.fxi_012_momentum_pullback.strategy import FXI012Strategy

register("fxi_012_momentum_pullback")(FXI012Strategy)
