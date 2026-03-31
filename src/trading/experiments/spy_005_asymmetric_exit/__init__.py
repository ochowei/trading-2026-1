"""SPY RSI(2) 非對稱出場均值回歸 (SPY-005)"""

from trading.experiments import register
from trading.experiments.spy_005_asymmetric_exit.strategy import (
    SPYAsymmetricExitStrategy,
)

register("spy_005_asymmetric_exit")(SPYAsymmetricExitStrategy)
