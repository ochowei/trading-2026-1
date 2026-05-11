"""INDA INDA-EEM 60d RS Divergence Filter on Multi-Period Capitulation MR (INDA-012)"""

from trading.experiments import register
from trading.experiments.inda_012_inda_eem_rs60d_divergence_mr.strategy import (
    INDA012Strategy,
)

register("inda_012_inda_eem_rs60d_divergence_mr")(INDA012Strategy)
