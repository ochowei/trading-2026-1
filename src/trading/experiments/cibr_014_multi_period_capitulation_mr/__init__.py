"""CIBR Multi-Period Capitulation-Strength Filter MR (CIBR-014)"""

from trading.experiments import register
from trading.experiments.cibr_014_multi_period_capitulation_mr.strategy import (
    CIBR014Strategy,
)

register("cibr_014_multi_period_capitulation_mr")(CIBR014Strategy)
