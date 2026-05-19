"""EWJ ^VIX Forward-Looking Implied-Vol Regime-Gated MR (EWJ-007)"""

from trading.experiments import register
from trading.experiments.ewj_007_vix_implied_vol_mr.strategy import EWJ007Strategy

register("ewj_007_vix_implied_vol_mr")(EWJ007Strategy)
