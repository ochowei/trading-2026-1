"""XBI Multi-Week Regime-Aware Pullback MR (XBI-015)"""

from trading.experiments import register
from trading.experiments.xbi_015_regime_pullback_mr.strategy import (
    XBI015RegimePullbackMRStrategy,
)

register("xbi_015_regime_pullback_mr")(XBI015RegimePullbackMRStrategy)
