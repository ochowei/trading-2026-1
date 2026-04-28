"""NVDA ADX-Filtered RSI(2) Mean Reversion (NVDA-010)"""

from trading.experiments import register
from trading.experiments.nvda_010_adx_rsi2_mr.strategy import (
    NVDA010ADXRsi2MRStrategy,
)

register("nvda_010_adx_rsi2_mr")(NVDA010ADXRsi2MRStrategy)
