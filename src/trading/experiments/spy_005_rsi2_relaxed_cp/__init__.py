"""SPY RSI(2) 放寬收盤位置均值回歸 (SPY-005)"""

from trading.experiments import register
from trading.experiments.spy_005_rsi2_relaxed_cp.strategy import (
    SPYRsi2RelaxedStrategy,
)

register("spy_005_rsi2_relaxed_cp")(SPYRsi2RelaxedStrategy)
