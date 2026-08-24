"""CIBR Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR (CIBR-016)"""

from trading.experiments import register
from trading.experiments.cibr_016_vol_level_gate_mr.strategy import CIBR016Strategy

register("cibr_016_vol_level_gate_mr")(CIBR016Strategy)
