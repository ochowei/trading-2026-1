"""EWZ–BRL Currency-Regime-Gated Vol-Transition MR (EWZ-010)"""

from trading.experiments import register
from trading.experiments.ewz_010_brl_regime_mr.strategy import (
    EWZ010BrlRegimeMRStrategy,
)

register("ewz_010_brl_regime_mr")(EWZ010BrlRegimeMRStrategy)
