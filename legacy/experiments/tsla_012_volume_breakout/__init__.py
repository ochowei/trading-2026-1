"""TSLA Volume-Confirmed BB Squeeze Breakout (TSLA-012)"""

from trading.experiments import register
from trading.experiments.tsla_012_volume_breakout.strategy import (
    TSLAVolumeBreakoutStrategy,
)

register("tsla_012_volume_breakout")(TSLAVolumeBreakoutStrategy)
