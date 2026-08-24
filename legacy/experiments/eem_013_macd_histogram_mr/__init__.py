"""EEM MACD Histogram Zero-Cross + Pullback Hybrid MR (EEM-013)"""

from trading.experiments import register
from trading.experiments.eem_013_macd_histogram_mr.strategy import EEM013Strategy

register("eem_013_macd_histogram_mr")(EEM013Strategy)
