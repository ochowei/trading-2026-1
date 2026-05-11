"""EEM ^VIX BANDS Regime Gate on Vol-Transition MR (EEM-018)"""

from trading.experiments import register
from trading.experiments.eem_018_vix_bands_mr.strategy import EEM018Strategy

register("eem_018_vix_bands_mr")(EEM018Strategy)
