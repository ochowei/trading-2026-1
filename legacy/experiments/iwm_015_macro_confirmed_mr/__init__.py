"""IWM Macro-Confirmed Capitulation MR (IWM-015)"""

from trading.experiments import register
from trading.experiments.iwm_015_macro_confirmed_mr.strategy import (
    IWM015Strategy,
)

register("iwm_015_macro_confirmed_mr")(IWM015Strategy)
