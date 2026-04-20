"""INDA CCI Oversold Reversal Mean Reversion (INDA-009)"""

from trading.experiments import register
from trading.experiments.inda_009_cci_oversold_mr.strategy import INDA009Strategy

register("inda_009_cci_oversold_mr")(INDA009Strategy)
