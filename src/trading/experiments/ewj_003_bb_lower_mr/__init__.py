"""EWJ BB Lower Band Mean Reversion (EWJ-003)"""

from trading.experiments import register
from trading.experiments.ewj_003_bb_lower_mr.strategy import EWJ003Strategy

register("ewj_003_bb_lower_mr")(EWJ003Strategy)
