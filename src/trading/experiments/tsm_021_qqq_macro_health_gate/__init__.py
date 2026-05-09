"""TSM-021: QQQ Macro-Health Gate on RS Momentum Pullback"""

from trading.experiments import register
from trading.experiments.tsm_021_qqq_macro_health_gate.strategy import (
    TSM021QQQMacroHealthGateStrategy,
)

register("tsm_021_qqq_macro_health_gate")(TSM021QQQMacroHealthGateStrategy)
