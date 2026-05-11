"""NVDA NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC (NVDA-021)"""

from trading.experiments import register
from trading.experiments.nvda_021_qqq_divergence_mbpc.strategy import (
    NVDA021QQQDivergenceMBPCStrategy,
)

register("nvda_021_qqq_divergence_mbpc")(NVDA021QQQDivergenceMBPCStrategy)
