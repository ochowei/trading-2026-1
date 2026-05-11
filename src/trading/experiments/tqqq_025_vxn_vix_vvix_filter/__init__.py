"""TQQQ VXN-VIX Cross-Index Divergence + VVIX Direction Filter (TQQQ-025)"""

from trading.experiments import register
from trading.experiments.tqqq_025_vxn_vix_vvix_filter.strategy import (
    TQQQ025VxnVixVvixStrategy,
)

register("tqqq_025_vxn_vix_vvix_filter")(TQQQ025VxnVixVvixStrategy)
