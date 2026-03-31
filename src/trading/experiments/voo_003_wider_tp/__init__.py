"""VOO RSI(2) 寬獲利目標均值回歸 (VOO-003)"""

from trading.experiments import register
from trading.experiments.voo_003_wider_tp.strategy import (
    VOOWiderTPStrategy,
)

register("voo_003_wider_tp")(VOOWiderTPStrategy)
