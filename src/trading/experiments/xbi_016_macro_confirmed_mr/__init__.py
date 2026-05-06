"""XBI Macro-Confirmed Pullback MR (XBI-016)"""

from trading.experiments import register
from trading.experiments.xbi_016_macro_confirmed_mr.strategy import (
    XBI016Strategy,
)

register("xbi_016_macro_confirmed_mr")(XBI016Strategy)
