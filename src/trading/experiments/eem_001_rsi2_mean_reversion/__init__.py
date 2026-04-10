"""EEM RSI(2) 均值回歸 (EEM-001)"""

from trading.experiments import register
from trading.experiments.eem_001_rsi2_mean_reversion.strategy import (
    EEMRsi2MeanReversionStrategy,
)

register("eem_001_rsi2_mean_reversion")(EEMRsi2MeanReversionStrategy)
