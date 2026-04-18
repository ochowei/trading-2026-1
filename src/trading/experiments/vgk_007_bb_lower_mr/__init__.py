"""VGK BB Lower Band Mean Reversion (VGK-007)"""

from trading.experiments import register
from trading.experiments.vgk_007_bb_lower_mr.strategy import VGK007Strategy

register("vgk_007_bb_lower_mr")(VGK007Strategy)
