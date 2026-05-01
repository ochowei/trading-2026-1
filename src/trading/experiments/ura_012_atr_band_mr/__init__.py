"""URA ATR Ratio BAND Mean Reversion (URA-012)"""

from trading.experiments import register
from trading.experiments.ura_012_atr_band_mr.strategy import URA012Strategy

register("ura_012_atr_band_mr")(URA012Strategy)
