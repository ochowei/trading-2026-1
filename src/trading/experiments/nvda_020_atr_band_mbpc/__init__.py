"""NVDA Volatility-Acceleration Band Filter on Multi-Week Regime-Aware MBPC (NVDA-020)"""

from trading.experiments import register
from trading.experiments.nvda_020_atr_band_mbpc.strategy import (
    NVDA020ATRBandMBPCStrategy,
)

register("nvda_020_atr_band_mbpc")(NVDA020ATRBandMBPCStrategy)
