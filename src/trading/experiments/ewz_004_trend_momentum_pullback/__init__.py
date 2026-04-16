"""EWZ Trend Momentum Pullback (EWZ-004)"""

from trading.experiments import register
from trading.experiments.ewz_004_trend_momentum_pullback.strategy import EWZ004Strategy

register("ewz_004_trend_momentum_pullback")(EWZ004Strategy)
