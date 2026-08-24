"""EWT Volatility-Regime-Gated RS Momentum Pullback (EWT-011)"""

from trading.experiments import register
from trading.experiments.ewt_011_vol_gated_rs_momentum.strategy import EWT011Strategy

register("ewt_011_vol_gated_rs_momentum")(EWT011Strategy)
