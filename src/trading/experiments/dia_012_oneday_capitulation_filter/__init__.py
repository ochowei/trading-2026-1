"""DIA Single-Day Capitulation-Depth Filter MR (DIA-012)"""

from trading.experiments import register
from trading.experiments.dia_012_oneday_capitulation_filter.strategy import (
    DIA012Strategy,
)

register("dia_012_oneday_capitulation_filter")(DIA012Strategy)
