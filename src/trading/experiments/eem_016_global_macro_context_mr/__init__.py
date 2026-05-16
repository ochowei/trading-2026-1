"""EEM Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR (EEM-016)"""

from trading.experiments import register
from trading.experiments.eem_016_global_macro_context_mr.strategy import (
    EEM016Strategy,
)

register("eem_016_global_macro_context_mr")(EEM016Strategy)
