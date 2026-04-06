"""GLD Donchian Channel Breakout (GLD-011)"""

from trading.experiments import register
from trading.experiments.gld_011_donchian_breakout.strategy import (
    GLDDonchianBreakoutStrategy,
)

register("gld_011_donchian_breakout")(GLDDonchianBreakoutStrategy)
