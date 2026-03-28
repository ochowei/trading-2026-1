"""USO 短窗口急跌均值回歸 (USO-007)"""

from trading.experiments import register
from trading.experiments.uso_007_sharp_pullback.strategy import (
    USOSharpPullbackStrategy,
)

register("uso_007_sharp_pullback")(USOSharpPullbackStrategy)
