"""XBI XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR (XBI-018)"""

from trading.experiments import register
from trading.experiments.xbi_018_xbi_xlv_divergence_mr.strategy import (
    XBI018XbiXlvDivergenceMRStrategy,
)

register("xbi_018_xbi_xlv_divergence_mr")(XBI018XbiXlvDivergenceMRStrategy)
