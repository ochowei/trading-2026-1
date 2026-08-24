"""EEM-020: Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combined Filter on Vol-Transition MR"""

from trading.experiments import register
from trading.experiments.eem_020_multi_anchor_combo_mr.strategy import EEM020Strategy

register("eem_020_multi_anchor_combo_mr")(EEM020Strategy)
