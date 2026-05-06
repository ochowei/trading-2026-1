"""USO ^OVX Implied-Volatility Forward-Looking Regime-Gated MR (USO-025)"""

from trading.experiments import register
from trading.experiments.uso_025_ovx_implied_vol_mr.strategy import (
    USO025Strategy,
)

register("uso_025_ovx_implied_vol_mr")(USO025Strategy)
