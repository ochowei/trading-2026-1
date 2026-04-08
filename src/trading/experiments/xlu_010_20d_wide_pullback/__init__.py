"""XLU Volatility-Spike Mean Reversion (XLU-010)"""

from trading.experiments import register
from trading.experiments.xlu_010_20d_wide_pullback.strategy import (
    XLUVolSpikeMRStrategy,
)

register("xlu_010_20d_wide_pullback")(XLUVolSpikeMRStrategy)
