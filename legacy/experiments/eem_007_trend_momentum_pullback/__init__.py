"""EEM Trend Momentum Pullback (EEM-007)"""

from trading.experiments import register
from trading.experiments.eem_007_trend_momentum_pullback.strategy import EEM007Strategy

register("eem_007_trend_momentum_pullback")(EEM007Strategy)
