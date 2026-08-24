"""USO ^OVX 5d Direction Multi-Window IV Regime Gate MR (USO-028)"""

from trading.experiments import register
from trading.experiments.uso_028_ovx_5d_direction_mr.strategy import USO028Strategy

register("uso_028_ovx_5d_direction_mr")(USO028Strategy)
