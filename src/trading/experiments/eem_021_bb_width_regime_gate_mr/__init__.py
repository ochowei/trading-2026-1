"""EEM-021: BB-Width Regime Gate on Vol-Transition MR"""

from trading.experiments import register
from trading.experiments.eem_021_bb_width_regime_gate_mr.strategy import EEM021Strategy

register("eem_021_bb_width_regime_gate_mr")(EEM021Strategy)
