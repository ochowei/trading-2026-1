"""XLU ^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR (XLU-014)"""

from trading.experiments import register
from trading.experiments.xlu_014_tnx_rate_direction_mr.strategy import (
    XLU014Strategy,
)

register("xlu_014_tnx_rate_direction_mr")(XLU014Strategy)
