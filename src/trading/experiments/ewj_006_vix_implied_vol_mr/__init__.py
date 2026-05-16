"""EWJ ^VIX Forward-Looking Implied-Vol Regime-Gated MR (EWJ-006)"""

from trading.experiments import register
from trading.experiments.ewj_006_vix_implied_vol_mr.strategy import EWJ006Strategy

register("ewj_006_vix_implied_vol_mr")(EWJ006Strategy)
