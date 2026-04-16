"""EWT Relative Strength Momentum Pullback (EWT-007)"""

from trading.experiments import register
from trading.experiments.ewt_007_rs_momentum.strategy import EWT007Strategy

register("ewt_007_rs_momentum")(EWT007Strategy)
