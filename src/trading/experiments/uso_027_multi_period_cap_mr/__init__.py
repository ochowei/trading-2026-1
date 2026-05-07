"""USO Multi-Period Capitulation-Strength Filter MR (USO-027)"""

from trading.experiments import register
from trading.experiments.uso_027_multi_period_cap_mr.strategy import USO027Strategy

register("uso_027_multi_period_cap_mr")(USO027Strategy)
