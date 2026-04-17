"""EEM BB Lower + Pullback Cap Hybrid Mean Reversion (EEM-012)"""

from trading.experiments import register
from trading.experiments.eem_012_bb_lower_pullback_cap.strategy import EEM012Strategy

register("eem_012_bb_lower_pullback_cap")(EEM012Strategy)
