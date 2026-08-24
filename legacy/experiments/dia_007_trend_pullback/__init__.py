"""DIA Trend Pullback to SMA(50) (DIA-007)"""

from trading.experiments import register
from trading.experiments.dia_007_trend_pullback.strategy import (
    DIATrendPullbackStrategy,
)

register("dia_007_trend_pullback")(DIATrendPullbackStrategy)
