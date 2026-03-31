"""URA 回檔 + RSI(2) 均值回歸 (URA-003)"""

from trading.experiments import register
from trading.experiments.ura_003_pullback_rsi2.strategy import (
    URAPullbackRSI2Strategy,
)

register("ura_003_pullback_rsi2")(URAPullbackRSI2Strategy)
