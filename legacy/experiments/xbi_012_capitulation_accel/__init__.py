"""XBI Capitulation + Acceleration Reversal (XBI-012)"""

from trading.experiments import register
from trading.experiments.xbi_012_capitulation_accel.strategy import (
    XBI012Strategy,
)

register("xbi_012_capitulation_accel")(XBI012Strategy)
