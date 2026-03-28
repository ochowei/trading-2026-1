"""USO 回檔範圍過濾 + RSI(2) + 2日急跌均值回歸 (USO-012)"""

from trading.experiments import register
from trading.experiments.uso_012_capped_pullback.strategy import (
    USOCappedPullbackStrategy,
)

register("uso_012_capped_pullback")(USOCappedPullbackStrategy)
