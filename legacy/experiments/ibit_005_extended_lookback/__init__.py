"""IBIT 20 日回看均值回歸 (IBIT-005)"""

from trading.experiments import register
from trading.experiments.ibit_005_extended_lookback.strategy import (
    IBIT005Strategy,
)

register("ibit_005_extended_lookback")(IBIT005Strategy)
