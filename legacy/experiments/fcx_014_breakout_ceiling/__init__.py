"""FCX Multi-Period Direction-Filter Regime Breakout (FCX-014)"""

from trading.experiments import register
from trading.experiments.fcx_014_breakout_ceiling.strategy import (
    FCX014BreakoutCeilingStrategy,
)

register("fcx_014_breakout_ceiling")(FCX014BreakoutCeilingStrategy)
