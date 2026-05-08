"""EEM DXY Direction Filter on Vol-Transition MR (EEM-016)"""

from trading.experiments import register
from trading.experiments.eem_016_dxy_direction_mr.strategy import EEM016Strategy

register("eem_016_dxy_direction_mr")(EEM016Strategy)
