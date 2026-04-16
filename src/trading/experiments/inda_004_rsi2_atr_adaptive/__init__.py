"""INDA Momentum Crash Mean Reversion (INDA-004)"""

from trading.experiments import register
from trading.experiments.inda_004_rsi2_atr_adaptive.strategy import (
    INDAMomentumCrashStrategy,
)

register("inda_004_rsi2_atr_adaptive")(INDAMomentumCrashStrategy)
