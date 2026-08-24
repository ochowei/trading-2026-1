"""VGK RSI(2) 均值回歸 (VGK-001)"""

from trading.experiments import register
from trading.experiments.vgk_001_rsi2_mean_reversion.strategy import (
    VGKRsi2MeanReversionStrategy,
)

register("vgk_001_rsi2_mean_reversion")(VGKRsi2MeanReversionStrategy)
