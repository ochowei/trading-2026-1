"""EWZ BB Lower Band + Pullback Cap Hybrid (EWZ-006)"""

from trading.experiments import register
from trading.experiments.ewz_006_bb_lower_pullback_cap.strategy import EWZ006Strategy

register("ewz_006_bb_lower_pullback_cap")(EWZ006Strategy)
