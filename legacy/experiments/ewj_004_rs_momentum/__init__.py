"""EWJ Relative Strength Momentum Pullback (EWJ-004)"""

from trading.experiments import register
from trading.experiments.ewj_004_rs_momentum.strategy import EWJ004Strategy

register("ewj_004_rs_momentum")(EWJ004Strategy)
