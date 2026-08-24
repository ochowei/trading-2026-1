"""TQQQ ^VIX Direction Filter on Vol-Regime-Gated Capitulation Buy (TQQQ-019)"""

from trading.experiments import register
from trading.experiments.tqqq_019_vix_direction_mr.strategy import (
    TQQQ019VixDirectionStrategy,
)

register("tqqq_019_vix_direction_mr")(TQQQ019VixDirectionStrategy)
