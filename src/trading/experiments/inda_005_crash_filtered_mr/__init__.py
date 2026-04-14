"""INDA 2-Day Crash Filtered Mean Reversion (INDA-005)"""

from trading.experiments import register
from trading.experiments.inda_005_crash_filtered_mr.strategy import INDA005Strategy

register("inda_005_crash_filtered_mr")(INDA005Strategy)
