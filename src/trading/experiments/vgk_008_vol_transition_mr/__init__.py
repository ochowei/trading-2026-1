"""VGK Post-Capitulation Vol-Transition MR (VGK-008)"""

from trading.experiments import register
from trading.experiments.vgk_008_vol_transition_mr.strategy import VGK008Strategy

register("vgk_008_vol_transition_mr")(VGK008Strategy)
