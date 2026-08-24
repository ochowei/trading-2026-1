"""INDA Exit-Optimized Mean Reversion (INDA-006)"""

from trading.experiments import register
from trading.experiments.inda_006_exit_optimized_mr.strategy import INDA006Strategy

register("inda_006_exit_optimized_mr")(INDA006Strategy)
