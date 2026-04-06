"""TSLA BB Wide Band Breakout (TSLA-009)"""

from trading.experiments import register
from trading.experiments.tsla_009_bb_wide_breakout.strategy import (
    TSLABBWideBreakoutStrategy,
)

register("tsla_009_bb_wide_breakout")(TSLABBWideBreakoutStrategy)
