"""VGK EURUSD Direction Filter on Vol-Transition MR (VGK-009)"""

from trading.experiments import register
from trading.experiments.vgk_009_eurusd_direction_mr.strategy import VGK009Strategy

register("vgk_009_eurusd_direction_mr")(VGK009Strategy)
