"""EEM Pullback + Williams %R Mean Reversion (EEM-004)"""

from trading.experiments import register
from trading.experiments.eem_004_pullback_wr.strategy import EEM004Strategy

register("eem_004_pullback_wr")(EEM004Strategy)
