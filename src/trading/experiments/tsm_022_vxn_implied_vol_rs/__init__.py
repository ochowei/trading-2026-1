"""TSM ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback (TSM-022)"""

from trading.experiments import register
from trading.experiments.tsm_022_vxn_implied_vol_rs.strategy import (
    TSMVXNImpliedVolRSStrategy,
)

register("tsm_022_vxn_implied_vol_rs")(TSMVXNImpliedVolRSStrategy)
