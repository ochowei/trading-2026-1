"""SOXL Signal-Day Capitulation-Strength CAP MR (SOXL-013)"""

from trading.experiments import register
from trading.experiments.soxl_013_signal_day_capitulation_cap.strategy import (
    SOXL013Strategy,
)

register("soxl_013_signal_day_capitulation_cap")(SOXL013Strategy)
