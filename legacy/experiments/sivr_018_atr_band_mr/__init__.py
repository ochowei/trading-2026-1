"""SIVR ATR Ratio BAND Mean Reversion (SIVR-018)"""

from trading.experiments import register
from trading.experiments.sivr_018_atr_band_mr.strategy import SIVR018Strategy

register("sivr_018_atr_band_mr")(SIVR018Strategy)
