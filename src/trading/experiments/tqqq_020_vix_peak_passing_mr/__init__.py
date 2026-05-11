"""TQQQ ^VIX Peak-Passing Filter on Vol-Regime-Gated Capitulation Buy (TQQQ-020)"""

from trading.experiments import register
from trading.experiments.tqqq_020_vix_peak_passing_mr.strategy import (
    TQQQ020VixPeakPassingStrategy,
)

register("tqqq_020_vix_peak_passing_mr")(TQQQ020VixPeakPassingStrategy)
