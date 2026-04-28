"""CIBR NR7 Volatility Contraction + Pullback MR (CIBR-010)"""

from trading.experiments import register
from trading.experiments.cibr_010_nr7_pullback_mr.strategy import (
    CIBR010Strategy,
)

register("cibr_010_nr7_pullback_mr")(CIBR010Strategy)
