"""XBI Gap-Down Capitulation + Intraday Reversal MR (XBI-013)"""

from trading.experiments import register
from trading.experiments.xbi_013_gap_reversal_mr.strategy import XBI013Strategy

register("xbi_013_gap_reversal_mr")(XBI013Strategy)
