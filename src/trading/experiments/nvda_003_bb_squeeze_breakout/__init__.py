"""NVDA Bollinger Band Squeeze Breakout (NVDA-003)"""

from trading.experiments import register
from trading.experiments.nvda_003_bb_squeeze_breakout.strategy import (
    NVDABBSqueezeBreakoutStrategy,
)

register("nvda_003_bb_squeeze_breakout")(NVDABBSqueezeBreakoutStrategy)
