"""NVDA Signal-Day 5d Return Ceiling on Multi-Week Regime-Aware MBPC (NVDA-017)"""

from trading.experiments import register
from trading.experiments.nvda_017_signal_day_filter.strategy import (
    NVDA017SignalDayFilterStrategy,
)

register("nvda_017_signal_day_filter")(NVDA017SignalDayFilterStrategy)
