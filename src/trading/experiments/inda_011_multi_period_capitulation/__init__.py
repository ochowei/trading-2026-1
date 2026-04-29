"""INDA Multi-Period Capitulation-Strength Filter MR (INDA-011)"""

from trading.experiments import register
from trading.experiments.inda_011_multi_period_capitulation.strategy import (
    INDA011Strategy,
)

register("inda_011_multi_period_capitulation")(INDA011Strategy)
