"""VOO RSI(2) 非對稱出場均值回歸 (VOO-002)"""

from trading.experiments import register
from trading.experiments.voo_002_asymmetric_exit.strategy import (
    VOOAsymmetricStrategy,
)

register("voo_002_asymmetric_exit")(VOOAsymmetricStrategy)
