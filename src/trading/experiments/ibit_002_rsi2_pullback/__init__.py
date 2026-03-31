"""IBIT RSI(2) + 回檔範圍均值回歸 (IBIT-002)"""

from trading.experiments import register
from trading.experiments.ibit_002_rsi2_pullback.strategy import (
    IBITRSI2PullbackStrategy,
)

register("ibit_002_rsi2_pullback")(IBITRSI2PullbackStrategy)
