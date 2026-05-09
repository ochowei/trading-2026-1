"""TSM ATR(5)/ATR(20) BAND filter on RS Momentum Pullback (TSM-018)"""

from trading.experiments import register
from trading.experiments.tsm_018_atr_band_rs.strategy import (
    TSMAtrBandRSStrategy,
)

register("tsm_018_atr_band_rs")(TSMAtrBandRSStrategy)
