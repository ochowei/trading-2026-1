"""EWZ ^VIX Forward-Looking Implied-Vol Regime-Gated MR (EWZ-008)"""

from trading.experiments import register
from trading.experiments.ewz_008_vix_implied_vol_mr.strategy import (
    EWZ008Strategy,
)

register("ewz_008_vix_implied_vol_mr")(EWZ008Strategy)
