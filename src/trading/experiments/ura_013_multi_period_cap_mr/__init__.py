"""URA Multi-Period Capitulation-Strength Filter MR (URA-013)"""

from trading.experiments import register
from trading.experiments.ura_013_multi_period_cap_mr.strategy import URA013Strategy

register("ura_013_multi_period_cap_mr")(URA013Strategy)
