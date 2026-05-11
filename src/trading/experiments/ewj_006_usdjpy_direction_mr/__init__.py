"""EWJ USDJPY Direction Filter on Vol-Transition MR (EWJ-006)"""

from trading.experiments import register
from trading.experiments.ewj_006_usdjpy_direction_mr.strategy import EWJ006Strategy

register("ewj_006_usdjpy_direction_mr")(EWJ006Strategy)
