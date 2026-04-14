"""CIBR 動量強化均值回歸 (CIBR-004)"""

from trading.experiments import register
from trading.experiments.cibr_004_rsi2_vol_adaptive.strategy import (
    CIBRRSI2VolAdaptiveStrategy,
)

register("cibr_004_rsi2_vol_adaptive")(CIBRRSI2VolAdaptiveStrategy)
