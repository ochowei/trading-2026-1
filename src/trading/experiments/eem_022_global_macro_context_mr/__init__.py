"""EEM Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR (EEM-022)"""

from trading.experiments import register
from trading.experiments.eem_022_global_macro_context_mr.strategy import (
    EEM022Strategy,
)

register("eem_022_global_macro_context_mr")(EEM022Strategy)
