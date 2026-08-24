"""EWZ Relative Strength Momentum Pullback (EWZ-005)"""

from trading.experiments import register
from trading.experiments.ewz_005_rs_momentum.strategy import EWZ005Strategy

register("ewz_005_rs_momentum")(EWZ005Strategy)
