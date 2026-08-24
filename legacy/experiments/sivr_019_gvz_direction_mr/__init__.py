"""SIVR GVZ Implied-Vol Direction Filter MR (SIVR-019)"""

from trading.experiments import register
from trading.experiments.sivr_019_gvz_direction_mr.strategy import SIVR019Strategy

register("sivr_019_gvz_direction_mr")(SIVR019Strategy)
