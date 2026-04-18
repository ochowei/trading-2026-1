"""VGK Trend Pullback Momentum (VGK-006)"""

from trading.experiments import register
from trading.experiments.vgk_006_trend_pullback_momentum.strategy import (
    VGK006Strategy,
)

register("vgk_006_trend_pullback_momentum")(VGK006Strategy)
