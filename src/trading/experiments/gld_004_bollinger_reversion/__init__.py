"""GLD 布林帶均值回歸 (GLD-004)"""

from trading.experiments import register
from trading.experiments.gld_004_bollinger_reversion.strategy import (
    GLDBollingerReversionStrategy,
)

register("gld_004_bollinger_reversion")(GLDBollingerReversionStrategy)
