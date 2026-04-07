"""GLD-010: Momentum Pullback (GLD Momentum Pullback Strategy)"""

from trading.experiments import register
from trading.experiments.gld_010_momentum_pullback.strategy import GLD010Strategy

register("gld_010_momentum_pullback")(GLD010Strategy)
