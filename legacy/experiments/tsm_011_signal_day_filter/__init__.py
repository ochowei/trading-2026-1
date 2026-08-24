"""TSM Signal-Day Direction Filter on RS Momentum Pullback (TSM-011)"""

from trading.experiments import register
from trading.experiments.tsm_011_signal_day_filter.strategy import (
    TSMSignalDayFilterStrategy,
)

register("tsm_011_signal_day_filter")(TSMSignalDayFilterStrategy)
