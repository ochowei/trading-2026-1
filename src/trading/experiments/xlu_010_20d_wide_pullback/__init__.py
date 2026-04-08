"""XLU 20-Day Wide Pullback + Williams %R + Reversal Candle (XLU-010)"""

from trading.experiments import register
from trading.experiments.xlu_010_20d_wide_pullback.strategy import (
    XLU20dWidePullbackStrategy,
)

register("xlu_010_20d_wide_pullback")(XLU20dWidePullbackStrategy)
