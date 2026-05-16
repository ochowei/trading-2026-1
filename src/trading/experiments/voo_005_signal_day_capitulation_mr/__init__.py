"""VOO Signal-Day Capitulation-Strength Filter MR (VOO-005)"""

from trading.experiments import register
from trading.experiments.voo_005_signal_day_capitulation_mr.strategy import (
    VOO005Strategy,
)

register("voo_005_signal_day_capitulation_mr")(VOO005Strategy)
