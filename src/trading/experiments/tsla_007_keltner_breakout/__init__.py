"""TSLA Keltner Channel Breakout (TSLA-007)"""

from trading.experiments import register
from trading.experiments.tsla_007_keltner_breakout.strategy import (
    TSLAKeltnerBreakoutStrategy,
)

register("tsla_007_keltner_breakout")(TSLAKeltnerBreakoutStrategy)
