"""IWM Pullback Range + RSI(2) Hybrid (IWM-010)"""

from trading.experiments import register
from trading.experiments.iwm_010_pullback_rsi2_hybrid.strategy import (
    IWM010Strategy,
)

register("iwm_010_pullback_rsi2_hybrid")(IWM010Strategy)
