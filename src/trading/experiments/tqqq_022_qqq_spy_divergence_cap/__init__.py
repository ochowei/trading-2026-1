"""TQQQ QQQ-SPY Cross-Asset Divergence FLOOR Regime-Gated Capitulation Buy (TQQQ-022)"""

from trading.experiments import register
from trading.experiments.tqqq_022_qqq_spy_divergence_cap.strategy import (
    TQQQ022QQQSPYDivergenceStrategy,
)

register("tqqq_022_qqq_spy_divergence_cap")(TQQQ022QQQSPYDivergenceStrategy)
