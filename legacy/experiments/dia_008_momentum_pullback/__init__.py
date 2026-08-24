"""DIA Momentum Pullback (DIA-008)"""

from trading.experiments import register
from trading.experiments.dia_008_momentum_pullback.strategy import (
    DIA008MomentumPullbackStrategy,
)

register("dia_008_momentum_pullback")(DIA008MomentumPullbackStrategy)
