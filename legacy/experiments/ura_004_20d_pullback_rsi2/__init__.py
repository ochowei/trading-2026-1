"""URA 20日回檔 + RSI(2) 均值回歸 (URA-004)"""

from trading.experiments import register
from trading.experiments.ura_004_20d_pullback_rsi2.strategy import (
    URA20dPullbackRSI2Strategy,
)

register("ura_004_20d_pullback_rsi2")(URA20dPullbackRSI2Strategy)
