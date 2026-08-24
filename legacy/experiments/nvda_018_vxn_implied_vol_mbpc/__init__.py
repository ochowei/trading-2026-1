"""NVDA ^VXN Implied-Volatility Forward-Looking Regime-Gated MBPC (NVDA-018)"""

from trading.experiments import register
from trading.experiments.nvda_018_vxn_implied_vol_mbpc.strategy import (
    NVDA018Strategy,
)

register("nvda_018_vxn_implied_vol_mbpc")(NVDA018Strategy)
