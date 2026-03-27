"""GLD 放寬 Keltner 通道均值回歸 (GLD-006)"""

from trading.experiments import register
from trading.experiments.gld_006_keltner_relaxed.strategy import (
    GLDRelaxedKeltnerReversionStrategy,
)

register("gld_006_keltner_relaxed")(GLDRelaxedKeltnerReversionStrategy)
