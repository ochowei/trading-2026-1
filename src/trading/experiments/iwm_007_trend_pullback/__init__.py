"""IWM Trend Pullback Recovery (IWM-007)"""

from trading.experiments import register
from trading.experiments.iwm_007_trend_pullback.strategy import (
    IWM007Strategy,
)

register("iwm_007_trend_pullback")(IWM007Strategy)
