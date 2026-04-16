"""CIBR 趨勢動量回調 (CIBR-007)"""

from trading.experiments import register
from trading.experiments.cibr_007_trend_momentum_pullback.strategy import (
    CIBRTrendMomentumStrategy,
)

register("cibr_007_trend_momentum_pullback")(CIBRTrendMomentumStrategy)
