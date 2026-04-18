"""INDA BB Lower Band + Pullback Cap Hybrid Mean Reversion (INDA-008)"""

from trading.experiments import register
from trading.experiments.inda_008_bb_lower_pullback_cap.strategy import INDA008Strategy

register("inda_008_bb_lower_pullback_cap")(INDA008Strategy)
