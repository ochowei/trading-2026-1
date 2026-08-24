"""DIA RSI(5) Trend Pullback (DIA-010)"""

from trading.experiments import register
from trading.experiments.dia_010_rsi5_trend_pullback.strategy import (
    DIARsi5TrendPullbackStrategy,
)

register("dia_010_rsi5_trend_pullback")(DIARsi5TrendPullbackStrategy)
