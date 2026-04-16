"""INDA Relative Strength Momentum Pullback (INDA-007)"""

from trading.experiments import register
from trading.experiments.inda_007_rs_momentum.strategy import INDA007Strategy

register("inda_007_rs_momentum")(INDA007Strategy)
