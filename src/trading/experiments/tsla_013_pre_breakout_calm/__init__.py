"""TSLA BB Squeeze Breakout + Pre-Breakout Calm Filter (TSLA-013)"""

from trading.experiments import register
from trading.experiments.tsla_013_pre_breakout_calm.strategy import (
    TSLAPreBreakoutCalmStrategy,
)

register("tsla_013_pre_breakout_calm")(TSLAPreBreakoutCalmStrategy)
