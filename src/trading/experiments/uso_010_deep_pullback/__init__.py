"""USO 深回檔 + RSI(2) + 2日急跌均值回歸 (USO-010)"""

from trading.experiments import register
from trading.experiments.uso_010_deep_pullback.strategy import (
    USODeepPullbackStrategy,
)

register("uso_010_deep_pullback")(USODeepPullbackStrategy)
