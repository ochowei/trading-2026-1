"""CIBR Momentum Breakout Pullback Continuation (CIBR-015)"""

from trading.experiments import register
from trading.experiments.cibr_015_momentum_pullback.strategy import (
    CIBR015Strategy,
)

register("cibr_015_momentum_pullback")(CIBR015Strategy)
