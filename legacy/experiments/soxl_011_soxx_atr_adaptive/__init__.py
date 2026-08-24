"""SOXL SOXX ATR-Adaptive Mean Reversion (SOXL-011)"""

from trading.experiments import register
from trading.experiments.soxl_011_soxx_atr_adaptive.strategy import (
    SOXLSoxxAtrStrategy,
)

register("soxl_011_soxx_atr_adaptive")(SOXLSoxxAtrStrategy)
