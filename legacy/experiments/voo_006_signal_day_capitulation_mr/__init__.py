"""VOO Signal-Day Capitulation-Strength Filter MR (VOO-006)"""

from trading.experiments import register
from trading.experiments.voo_006_signal_day_capitulation_mr.strategy import (
    VOO006Strategy,
)

register("voo_006_signal_day_capitulation_mr")(VOO006Strategy)
