"""FXI ATR Ratio BAND Mean Reversion (FXI-014)"""

from trading.experiments import register
from trading.experiments.fxi_014_atr_band_mr.strategy import FXI014Strategy

register("fxi_014_atr_band_mr")(FXI014Strategy)
