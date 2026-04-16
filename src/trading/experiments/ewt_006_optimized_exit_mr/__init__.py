"""EWT Optimized Exit Mean Reversion (EWT-006)"""

from trading.experiments import register
from trading.experiments.ewt_006_optimized_exit_mr.strategy import EWT006Strategy

register("ewt_006_optimized_exit_mr")(EWT006Strategy)
