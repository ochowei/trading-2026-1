"""SIVR RSI(2) + 回檔範圍均值回歸 (SIVR-004)"""

from trading.experiments import register
from trading.experiments.sivr_004_rsi2_pullback.strategy import (
    SIVRRSI2PullbackStrategy,
)

register("sivr_004_rsi2_pullback")(SIVRRSI2PullbackStrategy)
