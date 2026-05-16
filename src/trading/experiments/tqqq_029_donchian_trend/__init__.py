"""TQQQ Donchian Channel Trend-Following (TQQQ-native) (TQQQ-029)"""

from trading.experiments import register
from trading.experiments.tqqq_029_donchian_trend.strategy import (
    TQQQ029DonchianTrendStrategy,
)

register("tqqq_029_donchian_trend")(TQQQ029DonchianTrendStrategy)
