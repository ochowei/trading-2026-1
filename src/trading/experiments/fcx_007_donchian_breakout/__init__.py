"""FCX Donchian Channel Breakout (FCX-007)"""

from trading.experiments import register
from trading.experiments.fcx_007_donchian_breakout.strategy import (
    FCXDonchianBreakoutStrategy,
)

register("fcx_007_donchian_breakout")(FCXDonchianBreakoutStrategy)
