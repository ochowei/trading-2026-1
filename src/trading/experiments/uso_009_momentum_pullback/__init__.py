"""USO 回檔 + RSI(2) + 2日急跌均值回歸 (USO-009)"""

from trading.experiments import register
from trading.experiments.uso_009_momentum_pullback.strategy import (
    USOMomentumPullbackStrategy,
)

register("uso_009_momentum_pullback")(USOMomentumPullbackStrategy)
