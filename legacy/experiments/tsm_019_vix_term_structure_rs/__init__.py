"""TSM VIX Term-Structure Regime Gate on RS Momentum Pullback (TSM-019)"""

from trading.experiments import register
from trading.experiments.tsm_019_vix_term_structure_rs.strategy import TSM019Strategy

register("tsm_019_vix_term_structure_rs")(TSM019Strategy)
