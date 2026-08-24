"""EWT BB Lower Band + Pullback Cap Hybrid (EWT-008)"""

from trading.experiments import register
from trading.experiments.ewt_008_bb_lower_pullback_cap.strategy import EWT008Strategy

register("ewt_008_bb_lower_pullback_cap")(EWT008Strategy)
