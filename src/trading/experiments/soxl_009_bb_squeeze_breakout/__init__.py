"""SOXL BB 擠壓突破 + 成交模型 (SOXL BB Squeeze Breakout) — SOXL-009"""

from trading.experiments import register
from trading.experiments.soxl_009_bb_squeeze_breakout.strategy import (
    SOXLBBSqueezeBreakoutStrategy,
)

register("soxl_009_bb_squeeze_breakout")(SOXLBBSqueezeBreakoutStrategy)
