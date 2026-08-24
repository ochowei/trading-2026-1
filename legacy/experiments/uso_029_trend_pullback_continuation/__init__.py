"""USO Trend-Following Pullback Continuation (USO-029)"""

from trading.experiments import register
from trading.experiments.uso_029_trend_pullback_continuation.strategy import (
    USO029Strategy,
)

register("uso_029_trend_pullback_continuation")(USO029Strategy)
