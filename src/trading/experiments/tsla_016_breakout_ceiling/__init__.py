"""TSLA Multi-Period Direction-Filter Regime BB Squeeze Breakout (TSLA-016)"""

from trading.experiments import register
from trading.experiments.tsla_016_breakout_ceiling.strategy import (
    TSLA016BreakoutCeilingStrategy,
)

register("tsla_016_breakout_ceiling")(TSLA016BreakoutCeilingStrategy)
